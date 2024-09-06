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
      self.__status:str = self.__data['status']
    except:
      raise RuntimeError(f'WorldObject:__init__ for object{object_id}. Object source data does not contain required attributes.')

  @property
  def name(self):
    return self.__name

  @property
  def status(self):
    '''
    Provides the status of the object. It is advised to override this
    for more complex objects.
    '''
    return self.__status

  @property
  def id(self):
    return self.__id
