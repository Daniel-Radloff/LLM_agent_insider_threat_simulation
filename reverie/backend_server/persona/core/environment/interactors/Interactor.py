from abc import ABC, abstractmethod
from datetime import datetime
from typing import Callable, Union,Generator

from reverie.backend_server.persona.core.Personality import Personality
from reverie.backend_server.persona.core.planning.DailyPlanning import DailyPlanning
from reverie.backend_server.persona.models.model import Model
from reverie.backend_server.world.world_objects.WorldObject import WorldObject


class Interactor(ABC):
  # TODO: objects with hints is redundant because the object lists the
  #   availible commands
  def __init__(self,
               identifiers:list[str],
               daily_planner:DailyPlanning,
               personality:Personality,
               model : Model,
               time_func:Callable[[],datetime],
               ) -> None:
    '''
    identifiers are the ID's of the objects for which this interactor can
    interact with.

    options_with_hints are all the availible commands that are availible 
    to the LLM that it can use. Provide an operator along with hints on how to use it.
    Providing an explicit example is almost always the best way to go about it.

    All commands should only perform a single interaction with the target object.
    '''
    self.__identifiers = identifiers
    self._current_context = None
    self._model = model
    self.__engaged = False
    self._personality = personality
    self._daily_planner = daily_planner
    self._world_time = time_func

  def is_compatible(self,obj:WorldObject):
    '''
    Determines if this interactor is compatible with the target object.
    '''
    if obj.id in self.__identifiers:
      return True
    return False

  def inspect_object_closely(self,target:WorldObject):
    '''
    This is used to interact with objects that have more specific information. Such as computers.
    From the outside, ie: the eyes view of a object in the world, the WorldObject.status is called.
    You may want to change this behavior based on if the agent is interacting with the object.
    From the outside, a computer looks like its on, when interacting with it, it shows a more detailed
    status of what is on the screen.
    '''
    if self.is_compatible(target):
      return target.status
    else:
      raise ValueError(f"Incompatible object provided to get_object_status for class {type(self)}")

  @abstractmethod
  def interact_with(self,target:WorldObject):
    raise NotImplementedError()
  
  @abstractmethod
  def disengage(self):
    raise NotImplementedError()

  @property
  def engaged(self):
    '''
    This shows if we are busy with a object or not from a task.
    When a new action starts with a different object, or we do
    something else, the disengage routine must be called.
    '''
    return self.__engaged
