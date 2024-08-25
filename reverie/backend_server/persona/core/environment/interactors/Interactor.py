from abc import ABC, abstractmethod
from typing import Union,Generator

from reverie.backend_server.world.world_objects.WorldObject import WorldObject


class Interactor(ABC):
  def __init__(self,
               identifiers:list[str],
               options_with_hints:dict[str,str],
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
    self.__options = options_with_hints
    self.__current_action:Union[Generator,None] = None
    pass

  def set_action(self,target:WorldObject,action:str,parameters:Union[None,list[str]]=None):
    self.__current_action = self._select_generator(target,action,parameters)


  @abstractmethod
  def _select_generator(self,target:WorldObject,action:str,parameters:Union[None,list[str]])->Generator:
    '''
    Each class may have its own generators that perform actions.
    Set the generator and then return it. 
    The reason for this is so that actions can be interupted without worrying about world time.
    This may in future replace set_action entirely, but for now I'll keep it like this
    '''

  def is_compatible(self,obj:WorldObject):
    '''
    Determines if this interactor is compatible with the target object.
    '''
    if obj.id in self.__identifiers:
      return True
    return False

  def get_object_status(self,target:WorldObject):
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

  @property
  def finnished(self):
    '''
    On each access of finnished, the appropriate generator is called.
    If the generator has finnished execution, true is returned
    If the generator has not finnished execution, false is returned
    '''
    if self.__current_action is None:
      return True
    try:
      next(self.__current_action)
      return False
    except StopIteration:
      self.__current_action = None
      return True

  @property
  def commands(self):
    '''
    Returns all the commands that are availible for the agent to use:
    {"command" : "description and example"}
    '''
    return [pair for pair in self.__options.items()]

