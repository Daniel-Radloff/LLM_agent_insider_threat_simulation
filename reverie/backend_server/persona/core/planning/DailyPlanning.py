'''
Most data of a daily plan should be stored in the DailyPlanningData dataclass.
This is so that at the start of a new day, the data of the previous day can easily.
Be copied over and used for determining incomplete tasks, etc.

Tasks are Immutable except for setting the target, so it is safe to move them around
the system to be used as data for other methods in different objects.
'''
from dataclasses import dataclass, field
from itertools import chain
from datetime import datetime
from typing import Tuple, Union
from collections import deque
import os

from reverie.backend_server.persona.core.Concept import Concept
from reverie.backend_server.persona.core.LongTermMemory import LongTermMemory
from reverie.backend_server.persona.core.Personality import Personality
from reverie.backend_server.persona.core.ShortTermMemory import ShortTermMemory
from reverie.backend_server.persona.core.SpatialMemory import SpatialMemory
from reverie.backend_server.persona.core.helpers import no_validate, validate_hour_minute_time
from reverie.backend_server.persona.models.model import Model
from reverie.backend_server.world.world_objects.WorldObject import WorldObject

@dataclass(frozen=True)
class TimePeriod:
  start:datetime
  end:datetime

  def __contains__(self, time:datetime) ->bool:
    return self.start <= time < self.end

  def __str__(self) -> str:
    return f"{self.start}-{self.end}"

  def hour_min_str(self) -> str:
    return f"from {self.start.strftime("%H:%M")} to {self.end.strftime("%H:%M")}"

# ඞ
@dataclass
class Task:
  description:str
  target:Union[WorldObject,None] = field(default=None)

  def __str__(self) -> str:
    return f'{self.description}{f' using {self.target}' if self.target is not None else ''}'

@dataclass
class DailyPlanningData:
  wake_up_time:datetime
  # This includes variance, but is still subject to change.
  # This must be sorted
  schedule:list[Tuple[TimePeriod,Task]]
  incompleted_tasks:list[Task]

  def to_dict(self):
    return {
        'schedule' : [f'{time}: {task}'for time,task in self.schedule]
        }


class DailyPlanning:
  '''
  Is responsible for all planning on a daily basis.
  This includes determining wakeup times even though a 
  wakeup time is not strictly "planned".

  This uses logic originally from cognitive_modules/plan.py:_long_term_planning()
  However it contains some extensions to that logic.
  '''
  # Should we do short and long term memory or just one?
  def __init__(self, 
               llm:Model,
               personality:Personality,
               short_term_memory:ShortTermMemory,
               spatial_memory:SpatialMemory,
               standard_tasks:list[str],
               data: DailyPlanningData,
               previous_days_data:DailyPlanningData,
               current_steps:list[str]) -> None:
    self.__model = llm
    self.__personality  = personality
    self.__short_term_memory = short_term_memory
    self.__spatial_memory = spatial_memory
    self.__standard_tasks = standard_tasks
    self.__data = data
    self.__previous_day = previous_days_data
    self.__steps = deque(current_steps,maxlen=15)
    self._template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    pass


  # TODO what if something bad happens, maybe we should be 
  #   able to rethink how we are gonna approach the day
  def plan_for_today(self):
    '''
    Must be called at the very begining of a new day
    ie. 00:00

    TODO: this function is very messy and really long, there must
    be a better way to do this or consolidate things but for now
    'it is what it is'.
    '''
    self.__data.wake_up_time = self._wake_up_time()
    important_points = self._get_important_points()
    todays_broad_plan = self._get_broad_overview(important_points)

    # Using the basic plan for today we again look for relevant concepts related to each plan.
    # TODO Get only the most important point for each one, or the general most important points of all of them.

    original_plan = self._detailed_plan('\n'.join(todays_broad_plan))
    modified_plan = self._induce_variance(original_plan)
    new_schedule:list[Tuple[TimePeriod,Task]] = []
    for count, (time_slot, task) in enumerate(modified_plan):
      next = None
      if count != len(modified_plan) - 1:
        next = modified_plan[count][0]
      new_time,task = self._associate_object_with_task(time_slot,task,next)
      new_schedule.append((new_time,task))
    self.__data.schedule = new_schedule
    #TODO Originally, a thought would be generated here about the plan.
    # May or may not still do this.

  def simulate_day(self):
    '''
    Called at 00:00

    This function is used to simulate a day taking place
    entirely within the LLM.
    '''
    self.__data.wake_up_time = self._wake_up_time()
    important_points = self._get_important_points()
    todays_broad_plan = self._get_broad_overview(important_points)

    original_plan = self._detailed_plan('\n'.join(todays_broad_plan))
    modified_plan = self._induce_variance(original_plan)

    self.__data.schedule = modified_plan
    self._extrapulate_computer_interactions()
    print(self.__data.schedule)
    new_schedule:list[Tuple[TimePeriod,Task]] = []
    for count, (time_slot, task) in enumerate(self.__data.schedule):
      next = None
      if count != len(self.__data.schedule) - 1:
        next = self.__data.schedule[count][0]
      new_time,task = self._associate_object_with_task(time_slot,task,next)
      new_schedule.append((new_time,task))
    self.__data.schedule = new_schedule

  def _extrapulate_computer_interactions(self):
    '''
    This looks at the schedule for today and extrapulates all tasks that require
    interaction with a computer.
    Its not implimented in the best way from engineering standpoint. But its fine for now.
    '''
    def validate(response:str,_="")->str:
      if response.rstrip() not in ['yes','no']:
        raise ValueError(f'Invalid answer provided. Got:"{response}", expected: yes or no')
      return response 

    def flatten_schedule(schedule):
      flattened = []
      for item in schedule:
        if isinstance(item, list):  # Only flatten lists, leave tuples intact
          flattened.extend(item)
        else:
          flattened.append(item)
      return flattened

    with open(os.path.join(self._template_dir, "detect_computer_interaction.txt"),"r") as file:
        prompt = file.read()
    system_input = [self.__personality.get_summarized_identity()]
    example_output = "yes"
    fail_safe = "no"
    special_instruction = "Answer only in lowercase with either 'yes', or 'no'."
    new_schedule = []

    for time,action in self.__data.schedule:
      output = self.__model.run_inference(prompt,
                                          [action.description],
                                          system_input,
                                          example_output,
                                          validate,
                                          fail_safe,
                                          special_instruction=special_instruction)
      if output == 'yes':
        # create mini actions
        # take this task, and break it down into smaller components of how the task is going to be performed.
        complete_task = action.description
        detailed_plan = self._break_up_actions(complete_task+ f" {time.hour_min_str()}")
        detailed_plan = self._induce_variance(detailed_plan,True,time.hour_min_str())
        # either we can return the plan here and attach objects then, 
        # or we can modifiy the self.__data.schedule. That is probably the correct call in this situation.
        # for now, self.__data.schedule is modified in place.
        new_schedule.extend(detailed_plan)
      else:
        new_schedule.append((time,action))
    print(new_schedule)
    self.__data.schedule = flatten_schedule(new_schedule)
    print(self.__data.schedule)


  def _break_up_actions(self,action:str)->str:
    print(action)
    with open(os.path.join(self._template_dir, "deconstruct_high_level_action.txt"),"r") as file:
      prompt = file.read()
    prompt_input = [action]
    system_input = [self.__personality.get_summarized_identity()]
    example = f'''
13:00 <-> 13:07 <-> Open the weekly report document and review the sections completed in the previous sessions.
13:07 <-> 13:17 <-> Log into the project management tool and check for any new updates or data from team members or system reports.
13:17 <-> 13:33 <-> Input any new data from the project management tool into the report, updating sections like project milestones, task statuses, and progress metrics.
13:33 <-> 13:42 <-> Cross-reference this week’s report against last week’s to ensure that all progress is accurately reflected and major changes are captured.
13:42 <-> 13:58 <-> Adjust and update any charts or graphs in the report with the most recent data.
13:58 <-> 14:09 <-> Reformat the document to maintain consistent structure and layout, checking for font consistency and heading formats.
14:09 <-> 14:19 <-> Take a quick break from the computer to rest and refocus.
14:19 <-> 14:34 <-> Update the executive summary section with new key points from this week’s progress, including any challenges or accomplishments.
14:34 <-> 14:49 <-> Review the report for any incomplete sections or missing data, ensuring all objectives have been covered.
14:49 <-> 15:00 <-> Proofread the report for errors in grammar, spelling, and clarity.
15:00 <-> 15:04 <-> Save the report, back it up, and email the draft to your supervisor for feedback or approval.
    '''
    failsafe = 'ERROR'
    special_instruction = 'Place emphasis on actions that require interaction with work computers. Do NOT prefix, or postfix your answer, and adhear strictly to the format provided in the example. Do not pad your answer with extra newline characters. Do NOT exceed the time frame allocated to the task.'
    return self.__model.run_inference(prompt,
                                      prompt_input,
                                      system_input,
                                      example,
                                      self._validate_plan_format,
                                      failsafe,
                                      special_instruction=special_instruction,
                                      )

  def _wake_up_time(self)->datetime:
    date = self.__short_term_memory.get_current_time()
    if date.hour != 0 or date.minute != 0:
      raise RuntimeError(f"DailyPlanning.wake_up_time called when time is not 00:00 (start of a new day). Current time is: {date}")
      
    # TODO check project board
    with open(os.path.join(self._template_dir, "wake_up_hour.txt"),"r") as file:
        prompt = file.read()
    prompt_input = [self.__personality.lifestyle,
                    self.__personality.full_name]
    system_input = [self.__personality.get_summarized_identity()]
    example_output = "07:24"
    fail_safe = "06:00"
    special_instruction = "The time must be formatted according to 24 hour time. The output should only contain the time with no additional comments."
    output = self.__model.run_inference(prompt,
                                        prompt_input,
                                        system_input,
                                        example_output,
                                        validate_hour_minute_time,
                                        fail_safe,
                                        special_instruction=special_instruction)
    hour,minute = map(int,output.split(":"))
    return date.replace(hour=hour,minute=minute)


  def _get_important_points(self):
    important_events = self.__short_term_memory._generate_embedding(
        f"{self.__personality.full_name}'s plan for today")
    plan_for_today = self.__short_term_memory._generate_embedding(f"{self.__personality.full_name}'s plan for today.")
    retrieved_memories = self.__short_term_memory.retrieve_relevant_concepts([important_events,plan_for_today])
    event_descriptions = "\n".join([concept.description for concept in retrieved_memories])

    # TODO: refactor into a prompt file because this is disgusting.
    prompt=f"The following statements/memories contain potentialy useful information with regards to your day tommorow:\n{event_descriptions}\n is there anything here of importance that you want to keep in mind while planning your day? Write your response as notes to yourself."
    system_input = [self.__personality.get_summarized_identity()]
    example="Ron the HOD isn't very nice so I should spend as little time around the cafeteria as possible. Boss wants the project done by the end of the week. Im meeting with Sharon at 11:30 for brunch."
    fail_safe = "There is nothing special that demands my attention today."
    special_instruction = "If there is nothing special that demands your attention today, then you can respond with that"
    return self.__model.run_inference(prompt,
                                      [],
                                      system_input,
                                      example,
                                      no_validate,
                                      fail_safe,
                                      special_instruction=special_instruction)
  
  def _get_broad_overview(self,recent_knowledge:str,overwrite=False):
    '''
    we plan out our day according to:
    1. our normal day to day requirements
    2. the revised requirements based on our experiences
    3. the tasks that we meant to complete yesterday but were unable to?
    '''
    # Reason we use a numbered format is to make sure the llm is "thinking"
    def validate(response:str,_="")->str:
      lines = [line.rstrip() for line in response.split("\n")]
      actions = [line.split(")")[1] for line in lines]
      return ",".join(actions)

    date =  self.__short_term_memory.get_current_time()
    with open(os.path.join(self._template_dir, "daily_plan_outline.txt"),"r") as file:
      prompt = file.read()
    prompt_input = ["\n".join(self.__standard_tasks),
                    f"{date.year} {date.strftime("%B")} {date.day}",
                    f"{self.__data.wake_up_time.hour}:{self.__data.wake_up_time.minute}",
                    recent_knowledge]
    system_input = [self.__personality.get_summarized_identity()]
    wake_up_hour = self.__data.wake_up_time.hour
    example = f'''
1) Wake up and complete the morning routine at 06:30
2) Eat breakfast at 07:00
3) Work on the weekly report from 08:00 to 10:00
4) Attend the team meeting from 10:15 to 11:00
5) Review and finalize the project proposal from 11:15 to 12:00
6) Lunch break at 12:00
7) Continue working on the weekly report from 13:00 to 15:00
8) Submit the project proposal by 15:30
9) Wrap up any remaining tasks by 17:00
10) Relax and prepare for the next day starting at 18:00
    '''
    failsafe = 'eat breakfast at 7:00,read a book from 8:00 to 12:00,have lunch at 12:00,take a nap from 13:00 to 16:00,relax and watch TV from 19:00 to 20:00,go to bed at 23:00'
    # TODO refactor into own method because prompt will be lower quality
    special_instruction = "This plan that you generate now will replace and become your new default strategy, so don't make too drastic changes unless they are generally applicable."
    output = self.__model.run_inference(prompt,
                                        prompt_input,
                                        system_input,
                                        example,
                                        validate,
                                        failsafe,
                                        special_instruction if overwrite else  "Do NOT prefix your response with any comments."
                                        ).split(",")
    if overwrite:
      self.__standard_tasks = output
    return output

  def _validate_plan_format(self,response:str, _=""):
    tasks = [line.rstrip() for line in response.split("\n")]
    for task in tasks:
      parts = task.split("<->")
      if len(parts) != 3:
        print('plan validation failed')
        raise ValueError(f"Response has malformed task: {task}")
      start,end,_ = parts
      if validate_hour_minute_time(start.strip()) and validate_hour_minute_time(end.strip()):
        continue
      else:
        print('plan validation failed')
        raise ValueError(f"Response has malformed task: {task}")
    return response


  def _detailed_plan(self,plan_outline:str):
    '''
    Formulates a detailed plan for the agent to follow that guides their
    behavior. This plan is more a prediction, as it includes time
    variances that aim to simulate human behavior.
    '''
    embeddings = [self.__short_term_memory._generate_embedding(item) for item in plan_outline.split('\n')]
    most_important_concepts = self.__short_term_memory.retrieve_relevant_concepts(embeddings)
    most_important_points = [concept.description for concept in most_important_concepts]
    with open(os.path.join(self._template_dir, "detailed_plan.txt"),"r") as file:
      prompt = file.read()
    prompt_input = [self.__personality.full_name, plan_outline,'\n'.join(most_important_points)]
    example = '''
07:00 <-> 07:15 <-> Wake up and get out of bed
07:15 <-> 07:30 <-> Morning workout: Stretching exercises
07:30 <-> 08:00 <-> Morning workout: Cardio session
08:00 <-> 08:30 <-> Make and eat breakfast
08:30 <-> 09:00 <-> Commute to the office
09:00 <-> 09:30 <-> Team meeting: Project status updates
09:30 <-> 11:00 <-> Work on project report: Compile data and draft sections
11:00 <-> 11:30 <-> Client call: Discuss feedback on current deliverables
11:30 <-> 12:00 <-> Review and respond to emails
12:00 <-> 13:00 <-> Lunch break
13:00 <-> 14:30 <-> Continue working on project report: Refine and finalize draft
14:30 <-> 15:00 <-> Break and quick walk
15:00 <-> 16:00 <-> Review and organize notes from client call
16:00 <-> 17:00 <-> Follow up on action items from team meeting
17:00 <-> 17:30 <-> Wrap up work and prepare for the next day
17:30 <-> 18:00 <-> Commute back home
18:00 <-> 19:00 <-> Dinner
19:00 <-> 21:00 <-> Leisure time: Relax and unwind
21:00 <-> 22:00 <-> Prepare for bed and wind down
22:00 <-> 22:30 <-> Go to sleep
    '''
    special_instruction = "Do NOT prefix or postfix your response with anything other than the format specified by the example."
    # no failsafe for this stage
    failsafe = 'FAILURE'
    return self.__model.run_inference(prompt,
                                      prompt_input,
                                      [self.__personality.get_summarized_identity()],
                                      example,
                                      self._validate_plan_format,
                                      failsafe,
                                      special_instruction=special_instruction
                                      )


  def _induce_variance(self,plan:str,strict_time_bound=False,time_bound=""):
    '''
    Introduce variance into the response, through testing, it has been
    determined that placing this into a seperate prompt produces
    more consistent and superiour results
    '''
    to_return:list[Tuple[TimePeriod,Task]] = []
    with open(os.path.join(self._template_dir, f"introduce_variance{"_strict" if strict_time_bound else ""}.txt"),"r") as file:
      prompt = file.read()
    prompt_input = [plan,time_bound] if strict_time_bound else [plan]
    example = '''
06:25 <-> 07:00 <-> Wake up and complete morning routine
07:02 <-> 07:17 <-> Eat breakfast
08:05 <-> 09:55 <-> Work on the weekly report: Review project progress, gather data, and start drafting sections
09:58 <-> 10:13 <-> Break to get a drink and stretch
10:16 <-> 11:00 <-> Attend the team meeting: Discuss project updates, client feedback, and collaborate with team members
11:05 <-> 11:20 <-> Break to grab a snack
11:17 <-> 12:07 <-> Review and finalize the project proposal: Revise sections based on team feedback and comments from previous version
12:10 <-> 13:00 <-> Lunch break
13:02 <-> 14:32 <-> Continue working on the weekly report: Refine data analysis, add visualizations, and make any necessary changes to draft sections
14:35 <-> 15:05 <-> Break and review project proposal for finalization
15:10 <-> 16:30 <-> Finalize and submit the project proposal: Make sure all requirements are met and document is perfect before submission
16:32 <-> 17:00 <-> Wrap up any remaining tasks: Respond to urgent emails, update project management tool, and make sure everything is up-to-date
17:05 <-> 18:10 <-> Relax and prepare for the next day: Take a break, recharge, and get ready for tomorrow's tasks
    '''
    # no failsafe for this stage
    failsafe = 'FAILURE'
    special_instruction = "Do NOT prefix or postfix your response with anything other than the format specified by the example."
    if strict_time_bound:
      special_instruction = special_instruction + " Do NOT change the START time of the first task, and the END time of the last task."
      
    response = self.__model.run_inference(prompt,
                                          prompt_input,
                                          [self.__personality.get_summarized_identity()],
                                          example,
                                          self._validate_plan_format,
                                          failsafe,
                                          special_instruction=special_instruction
                                          )

    tasks = [line.strip() for line in response.split('\n')]
    current_time = self.__short_term_memory.get_current_time()
    for task in tasks:
      start,end,desc = [component.strip() for component in task.split('<->')]
      start_hour,start_minute = map(int, start.split(":"))
      end_hour,end_minute = map(int,end.split(":"))
      time = TimePeriod(
          current_time.replace(hour=start_hour, minute=start_minute),
          current_time.replace(hour=end_hour, minute=end_minute)
          )
      new_task = Task(
          desc
          )
      to_return.append((time,new_task))
    return to_return

  # TODO, this funciton for now just returns the object, it doesn't adjust times
  # based on the object distance etc.
  # TODO, this should maybe be used later down the line instead of when the
  # tasks are initialized.
  def _associate_object_with_task(self,
                                  allocated_time_period:TimePeriod,
                                  task:Task,
                                  next_time:Union[TimePeriod,None],
                                  )->Tuple[TimePeriod,Task]:
    '''
    this is probably not the best place for this function but oh well.
    What needs to happen is, we need to look at the time allocated for us, and also look at the time when the next task is planned to start.
    '''
    ''' 
    i send them for now to the LLM in a prompt asking it which object it wants to use.
        we have times and descriptions.
        and we should be able to return them. (lets return them as a tuple)

        Should I add distances? distances in minutes?
        (That way, i can account for distance during the schedule process.)
    once it decides on the object, I associate the task with the object.
    '''
    availible_objects = self.__spatial_memory.get_known_objects()
    current_location = self.__spatial_memory.current_location
    object_names = [obj[0].name for obj in availible_objects]
    def validate(response:str,_:str)->str:
      compare = response.strip()
      if compare in object_names:
        return compare
      elif compare == "None":
        return compare
      else:
        raise ValueError("Response does not correspond with one of the availible objects")

    with open(os.path.join(self._template_dir, "associate_object_with_task.txt"),"r") as file:
      prompt = file.read()
      prompt_input = [task.description,"\n".join(object_names)]
    example_response = object_names[0]
    special_instruction = "If there is no relevant object (such as if the task requires a talk in person with someone else), write: 'None' as your response."
    failsafe = "None"

    response = self.__model.run_inference(prompt,
                                          prompt_input,
                                          [self.__personality.get_summarized_identity()],
                                          example_response,
                                          validate,
                                          failsafe,
                                          special_instruction=special_instruction)
    
    # TODO: Impliment some kind of movement constant to calculate travel distances.
    if response == "None":
      return (allocated_time_period, task)
    else:
      index = object_names.index(response)
      selected_object = availible_objects[index][0]
      task.target = selected_object
      return (allocated_time_period, task)

  def determine_next_action(self):
    '''
    Determine if we should use an object, talk, or move etc to complete the next step in what we are doing.
    '''

    raise NotImplementedError()

  def to_dict(self):
    return {
        'current' : self.__data.to_dict(),
        'previous' : self.__previous_day.to_dict(),
        'standard' : self.__standard_tasks
        }

  @property
  def current_task(self):
    '''
    Returns the first task for which the current_time is
    with in the bounds of the tasks TimePeriod.
    '''
    for time,task in self.__data.schedule:
      if self. __short_term_memory.get_current_time() in time:
        return task
    return None

  @property
  def next_task(self):
    '''
    Returns the first task for which the current_time is
    with in the bounds of the tasks TimePeriod.
    '''
    for (time,task) in self.__data.schedule:
      if self. __short_term_memory.get_current_time() in time:
        return task
  
  def state(self):
    def return_schedule(x):
      return [
          {
            "start" : time.start,
            "end" : time.end,
            "description" : task.description,
            **({"target": task.target} if task.target is not None else {})
          } for time,task in x
        ]

    def return_incompleted(x):
      return [
          {
            "description" : task.description,
            **({"target": task.target} if task.target is not None else {})
          } for task in x
        ]

    return {
        "standard_tasks" : self.__standard_tasks,
        "data" : {
          "wake_up_time" : self.__data.wake_up_time,
          "schedule" : return_schedule(self.__data.schedule),
          "incompleted_tasks" : return_incompleted(self.__data.incompleted_tasks)
        },
        "previous" : {
          "wake_up_time" : self.__previous_day.wake_up_time,
          "schedule" : return_schedule(self.__previous_day.schedule),
          "incompleted_tasks" : return_incompleted(self.__previous_day.schedule)
        },
        "steps" : list(self.__steps)
      }
