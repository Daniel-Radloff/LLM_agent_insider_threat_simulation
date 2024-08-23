'''
Defines the object_classes dictionary, which is used during the initialization of the Tile class in order to programatically determine which implimentation of WorldObject to initialize based on the id provided.
'''
from collections.abc import Callable

from reverie.backend_server.world.world_objects.WorldObject import WorldObject

def default_object(id:str,name:str,data:dict):
  return WorldObject(id,name,data)

object_classes:dict[str,Callable[[str,str,dict],WorldObject]] = {
    'default' : default_object
    }
