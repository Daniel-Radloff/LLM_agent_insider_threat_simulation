'''
Most data of a daily plan should be stored in the DailyPlanningData dataclass.
This is so that at the start of a new day, the data of the previous day can easily.
Be copied over and used for determining incomplete tasks, etc.

Tasks are Immutable except for setting the target, so it is safe to move them around
the system to be used as data for other methods in different objects.
'''
from dataclasses import dataclass, field
from datetime import datetime
from typing import Union

from reverie.backend_server.persona.core.Concept import Concept
from reverie.backend_server.persona.core.LongTermMemory import LongTermMemory
from reverie.backend_server.persona.core.Personality import Personality
from reverie.backend_server.persona.core.ShortTermMemory import ShortTermMemory
from reverie.backend_server.persona.core.helpers import no_validate, validate_hour_minute_time
from reverie.backend_server.persona.models.model import Model
from reverie.backend_server.world.world_objects.WorldObject import WorldObject

@dataclass(frozen=True)
class TimePeriod:
  start:datetime
  end:datetime

  def __contains__(self, time:datetime) ->bool:
    return self.start <= time < self.end

# ඞ
@dataclass
class Task:
  description:str
  target:Union[WorldObject,None] = field(default=None)

@dataclass
class DailyPlanningData:
  wake_up_time:datetime
  # This includes variance, but is still subject to change.
  # This must be sorted
  schedule:dict[TimePeriod,Task]
  incompleted_tasks:list[Task]


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
               long_term_memory:LongTermMemory,
               short_term_memory:ShortTermMemory,
               standard_tasks:list[str],
               data: DailyPlanningData,
               previous_days_data:DailyPlanningData) -> None:
    self.__model = llm
    self.__personality  = personality
    self.__long_term_memory = long_term_memory
    self.__short_term_memory = short_term_memory
    self.__standard_tasks = standard_tasks
    self.__data = data
    self.__previous_day = previous_days_data
    pass


  def _wake_up_time(self)->datetime:
    '''
    Must be called at the very begining of a new day
    ie. 00:00
    '''
    date = self.__long_term_memory.get_current_time()
    if date.hour != 0 or date.minute != 0:
      raise RuntimeError(f"DailyPlanning.wake_up_time called when time is not 00:00 (start of a new day). Current time is: {date}")
      
    # TODO check project board
    with open("daily_planning_templates/wake_up_hour.txt","r") as file:
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
    # Validated by validate_hour_minute_time
    hour,minute = map(int,output.split(":"))
    # return new datetime object with wakeup time.
    return date.replace(hour=hour,minute=minute)

  # TODO what if something bad happens, maybe we should be 
  #   able to rethink how we are gonna approach the day
  def plan_for_today(self):
    # First, relevant memories related to planning are retrieved.
    important_events = self.__short_term_memory._generate_embedding(
        f"{self.__personality.full_name}'s plan for today")
    plan_for_today = self.__short_term_memory._generate_embedding(f"{self.__personality.full_name}'s plan for today.")
    
    retrieved_memories = self.__short_term_memory.retrieve_relevant_concepts([important_events,plan_for_today])

    # Next, the most relevant concepts are passed into a prompt to determine things we should be aware of when going about our day.

    #Seperating the process into two different calls will be slower but should (i speculate) provide better results.
    event_descriptions = "\n".join([concept.description for concept in retrieved_memories])

    prompt=f"The following statements/memories contain potentialy useful information with regards to your day tommorow:\n{event_descriptions}\n is there anything here of importance that you want to keep in mind while planning your day? Write your response as notes to yourself."
    system_input = [self.__personality.get_summarized_identity()]
    example="Ron the HOD isn't very nice so I should spend as little time around the cafeteria as possible. Boss wants the project done by the end of the week. Im meeting with Sharon at 11:30 for brunch."
    fail_safe = "There is nothing special that demands my attention today."
    special_instruction = "If there is nothing special that demands your attention today, then you can respond with that"
    important_points = self.__model.run_inference(prompt,
                                                  [],
                                                  system_input,
                                                  example,
                                                  no_validate,
                                                  fail_safe,
                                                  special_instruction=special_instruction)
    # Next, using our memories and revised notes on what we think we should watch out for,
    #   we plan out our day according to:
    #   1. our normal day to day requirements
    #   2. the revised requirements based on our experiences
    #   3. the tasks that we meant to complete yesterday but were unable to?

    todays_broad_plan = self.get_broad_overview(important_points)
    # Using the basic plan for today we again look for relevant concepts related to each plan.
    # TODO Get only the most important point for each one, or the general most important points of all of them.
    embeddings = [self.__short_term_memory._generate_embedding(item) for item in todays_broad_plan]
    most_important_concepts = self.__short_term_memory.retrieve_relevant_concepts(embeddings)
    most_important_points = [concept.description for concept in most_important_concepts]

    original_plan = self._detailed_plan(
        '\n'.join(todays_broad_plan),
        '\n'.join(most_important_points))
    self.__data.schedule = self._induce_variance(original_plan)

    #TODO Originally, a thought would be generated here about the plan.
    # May or may not still do this.

  def get_broad_overview(self,recent_knowledge:str,overwrite=False):
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
    with open("daily_planning_templates/daily_plan_outline.txt","r") as file:
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
    special_instruction = "This plan that you generate now will replace and become your new default strategy, so don't make too drastic changes unless they are generally applicable."
    output = self.__model.run_inference(prompt,
                                        prompt_input,
                                        system_input,
                                        example,
                                        validate,
                                        failsafe,
                                        special_instruction if overwrite else None
                                        ).split(",")
    if overwrite:
      self.__standard_tasks = output
    return output

  def _validate_plan_format(self,response:str, _=""):
    def validate_time(time:str)->bool:
      '''
      Assumes that the time is .strip()'d
      '''
      numbers = time.split(':')
      if len(numbers) != 2:
        raise ValueError("Time does not contain a ':' character")
      hours,minutes = numbers
      if int(hours) < 24 and int(hours) >= 0 and int(minutes) < 60 and int(minutes) >= 0:
        return True
      else:
        raise ValueError(f"Time is malformed '{hours}:{minutes}'")

    tasks = [line.rstrip() for line in response.split("\n")]
    for task in tasks:
      parts = task.split("<->")
      if len(parts) != 3:
        raise ValueError(f"Response has malformed task: {task}")
      start,end,_ = parts
      if validate_time(start.strip()) and validate_time(end.strip()):
        continue
      else:
        raise ValueError(f"Response has malformed task: {task}")
    return response


  def _detailed_plan(self,plan_outline:str, important_concepts:str):
    '''
    Formulates a detailed plan for the agent to follow that guides their
    behavior. This plan is more a prediction, as it includes time
    variances that aim to simulate human behavior.
    '''
    with open("daily_planning_templates/detailed_plan.txt","r") as file:
      prompt = file.read()
    prompt_input = [plan_outline,important_concepts]
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
    # no failsafe for this stage
    failsafe = 'FAILURE'
    return self.__model.run_inference(prompt,
                                      prompt_input,
                                      [self.__personality.get_summarized_identity()],
                                      example,
                                      self._validate_plan_format,
                                      failsafe,
                                      )


  def _induce_variance(self,plan:str):
    '''
    Introduce variance into the response, through testing, it has been
    determined that placing this into a seperate prompt produces
    more consistent and superiour results
    '''
    to_return:dict[TimePeriod,Task] = dict()
    with open("daily_planning_templates/introduce_variance.txt","r") as file:
      prompt = file.read()
    prompt_input = [plan]
    example = '''
06:25 <-> 07:00 <-> Wake up and complete morning routine
07:02 <-> 07:17 <-> Eat breakfast
08:05 <-> 09:55 <-> Work on the weekly report: Review project progress, gather data,
and start drafting sections
09:58 <-> 10:13 <-> Break to get a drink and stretch
10:16 <-> 11:00 <-> Attend the team meeting: Discuss project updates, client
feedback, and collaborate with team members
11:05 <-> 11:20 <-> Break to grab a snack
11:17 <-> 12:07 <-> Review and finalize the project proposal: Revise sections based
on team feedback and comments from previous version
12:10 <-> 13:00 <-> Lunch break
13:02 <-> 14:32 <-> Continue working on the weekly report: Refine data analysis, add
visualizations, and make any necessary changes to draft sections
14:35 <-> 15:05 <-> Break and review project proposal for finalization
15:10 <-> 16:30 <-> Finalize and submit the project proposal: Make sure all
requirements are met and document is perfect before submission
16:32 <-> 17:00 <-> Wrap up any remaining tasks: Respond to urgent emails, update
project management tool, and make sure everything is up-to-date
17:05 <-> 18:10 <-> Relax and prepare for the next day: Take a break, recharge, and
get ready for tomorrow's tasks
    '''
    # no failsafe for this stage
    failsafe = 'FAILURE'
      
    response = self.__model.run_inference(prompt,
                                        prompt_input,
                                        [self.__personality.get_summarized_identity()],
                                        example,
                                        self._validate_plan_format,
                                        failsafe,
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
      to_return[time] = new_task

    return to_return

  @property
  def current_task(self):
    '''
    Returns the first task for which the current_time is
    with in the bounds of the tasks TimePeriod.
    '''
    for time,task in self.__data.schedule.items():
      if self. __short_term_memory.get_current_time() in time:
        return task

  @property
  def next_task(self):
    '''
    Returns the first task for which the current_time is
    with in the bounds of the tasks TimePeriod.
    '''
    for time,task in self.__data.schedule.items():
      if self. __short_term_memory.get_current_time() in time:
        return task
