
from abc import ABC

from reverie.backend_server.world.world_objects.WorldObject import WorldObject


class Interactor(ABC):
  def __init__(self,
               identifiers:list[str],
               options_with_hints:dict[str,str],
               default_tickrate=30) -> None:
    '''
    identifiers are the ID's of the objects for which this interactor can
    interact with.

    options_with_hints are all the availible commands that are availible 
    to the LLM that it can use. Provide an operator along with hints on how to use it.
    Providing an explicit example is almost always the best way to go about it.
    '''
    self.__identifiers = identifiers
    self.__options = options_with_hints
    self.__default_tickrate = default_tickrate
    # When we are finnished, set to true
    self.__disengage = False
    pass

  @property
  def commands(self):
    '''
    Returns all the 
    '''

  def is_compatible(self,obj:WorldObject):
    '''
    Determines if this interactor is compatible with the target object.
    '''
    if obj.id in self.__identifiers:
      return True
    return False

  @property
  def finnished(self):
    return self.__disengage
