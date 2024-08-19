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
from reverie.backend_server.persona.core.LongTermMemory import LongTermMemory
from reverie.backend_server.persona.core.Personality import Personality
from reverie.backend_server.persona.core.helpers import validate_hour_minute_time
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
  def __init__(self, llm:Model, personality:Personality, long_term_memory:LongTermMemory) -> None:
    self.__model = llm
    self.__personality  = personality
    self.__memory = long_term_memory
    pass


  def wake_up_time(self)->datetime:
    '''
    Must be called at the very begining of a new day
    ie. 00:00
    '''
    date = self.__memory.get_current_time()
    if date.hour != 0 or date.minute != 0:
      raise RuntimeError(f"DailyPlanning.wake_up_time called when time is not 00:00 (start of a new day). Current time is: {date}")
      
    # TODO check project board
    prompt_input = [self.__personality.lifestyle,
                    self.__personality.full_name]
    system_input = [self.__personality.get_summarized_identity()]
    example_output = "07:24"
    fail_safe = "06:00"
    special_instruction = "The time must be formatted according to 24 hour time. The output should only contain the time with no additional comments."
    output = self.__model.run_inference("daily_planning_templates/wake_up_hour.txt",
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
