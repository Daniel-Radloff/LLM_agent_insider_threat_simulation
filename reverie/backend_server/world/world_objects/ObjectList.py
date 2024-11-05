'''
Defines the object_classes dictionary, which is used during the initialization of the Tile class in 
order to programatically determine which implimentation of WorldObject to initialize based on the id provided.
'''
from collections.abc import Callable

from reverie.backend_server.world.world_objects.Computer import Computer
from reverie.backend_server.world.world_objects.WorldObject import WorldObject

def default_object(id:str,data:dict):
  return WorldObject(id,data)
def computer(id:str,data:dict):
  return Computer(id,data)

object_class_initializers:dict[str,Callable[[str,dict],WorldObject]] = {
    'default' : default_object,
    '73621' : computer
    }
