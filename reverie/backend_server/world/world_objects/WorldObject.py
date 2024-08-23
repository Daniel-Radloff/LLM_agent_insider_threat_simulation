class WorldObject:
  '''
  This represents objects inside of the world.
  All non default objects must be registered under world_objects/ObjectList.py:object_classes using a function that calls the objects initializer.
  '''
  def __init__(self,
               object_id:str,
               name:str,
               data:dict,
               ) -> None:
    self.__id = object_id 
    self.__name = name
    self.__data = data
