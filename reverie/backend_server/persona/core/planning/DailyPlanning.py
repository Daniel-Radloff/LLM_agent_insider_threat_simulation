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

from reverie.backend_server.World import InteractableObject
from reverie.backend_server.persona.core.Concept import Concept
from reverie.backend_server.persona.core.LongTermMemory import LongTermMemory
from reverie.backend_server.persona.core.Personality import Personality
from reverie.backend_server.persona.core.ShortTermMemory import ShortTermMemory
from reverie.backend_server.persona.core.helpers import no_validate, validate_hour_minute_time
from reverie.backend_server.persona.models.model import Model

# ඞ
@dataclass(frozen=True)
class Task:
  description:str
  _target:Union[InteractableObject,None] = field(default=None)

  @property
  def target(self):
    return self._target
  
  # Reason why it should only be called once is so that the
  #   agent can be penalized/feel stupid/feel bad for making
  #   a mistake.
  @target.setter
  def set_target(self, target:InteractableObject):
    if self.target == None:
      object.__setattr__(self, '_target',target)
    else:
      raise RuntimeError("set_target, should under no circumstances be called twice")

@dataclass
class DailyPlanningData:
  wake_up_time:datetime
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
    todays_broad_plan = self.summarize_day_plan(important_points)
    pass

  def summarize_day_plan(self,recent_knowledge:str,overwrite=False):
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
    1) wake up and complete the morning routine at {wake_up_hour}:00,
    2) eat breakfast at {wake_up_hour+1}:00,
    3) work on company balance sheets from {wake_up_hour+2}:00 to {wake_up_hour+4}:00,
    4) ...
    '''
    failsafe = '''
    eat breakfast at 7:00 am,
    read a book from 8:00 am to 12:00 pm,
    have lunch at 12:00 pm,
    take a nap from 1:00 pm to 4:00 pm,
    relax and watch TV from 7:00 pm to 8:00 pm,
    go to bed at 11:00 pm
    '''
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


