'''
This module is responsible for the navigation of the map including path 
finding
'''
from reverie.backend_server.world.World import Tile, World
from reverie.backend_server.persona.core.SpatialMemory import SpatialMemory
from reverie.backend_server.persona.Agent import Agent


class Legs:
  def __init__(self,world:World,spatial_memory:SpatialMemory,body:Agent) -> None:
    self.__world = world
    self.__spatial_memory = spatial_memory
    self.__agent = body
    pass

  def move(self,tile:Tile)->int:
    '''
    This method will be used to modify distances based on terrain and 
    other factors. For now, it just steps to the next tile.
    Returns the amount of ticks a movement takes place over.
    '''
    current_tile = self.__spatial_memory.current_location
    current_tile._remove_agent(self.__agent)
    tile._add_agent(self.__agent)
    return 1
