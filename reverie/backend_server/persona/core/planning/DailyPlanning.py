'''
Most data of a daily plan should be stored in the DailyPlanningData dataclass.
This is so that at the start of a new day, the data of the previous day can easily.
Be copied over and used for determining incomplete tasks, etc.

Tasks are Immutable except for setting the target, so it is safe to move them around
the system to be used as data for other methods in different objects.
'''
from dataclasses import dataclass, field
from typing import Union

from reverie.backend_server.World import InteractableObject

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
  def __init__(self) -> None:
    pass
