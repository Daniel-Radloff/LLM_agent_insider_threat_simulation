from datetime import datetime
from typing import Callable, Union


class WorldObject:
  '''
  This represents objects inside of the world. All non default objects must be
  registered under world_objects/ObjectList.py:object_classes using a function
  that calls the objects initializer.
  '''
  def __init__(self,
               object_id:str,
               data:dict,
               ) -> None:
    self.__id = object_id 
    try:
      self.__name:str = data['name']
      self.__data = data
      self._status:str = self.__data.get('status','idle')
    except:
      raise RuntimeError(f'WorldObject:__init__ for object{object_id}. Object source data does not contain required attributes.')

  def interact(self,input:Union[str,None]=None)->str:
    if input is None:
      return f'You observe: {self.__name}'
    else:
      return f'You "{input}" using: {self.__name}'

  def attach_time(self,time_func:Callable[[],datetime]):
    self._world_time = time_func

  @property
  def current_world_time(self):
    return self._world_time()

  @property
  def object_time(self):
    return self._world_time()

  @property
  def availible_actions(self)->str:
    return 'Any action you want'

  @property
  def name(self):
    return self.__name

  @property
  def status(self):
    '''
    Provides the status of the object. It is advised to override this
    for more complex objects.
    '''
    return self._status

  @property
  def ready_for_interaction(self)->bool:
    return True

  @property
  def id(self):
    return self.__id
