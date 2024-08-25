'''
In the original code, spatial memory existed as a way to tie events to the game world.
With an object oriented approach, a colegue has suggested that I do away with this
in favor for conceptualizing the entire world and all information about it within the
Concept objects.
For now, this class will remain just to get the project to a workable state.
'''
from typing import Tuple

from numpy.lib import math
from reverie.backend_server.persona.Agent import Agent
from reverie.backend_server.world.World import Tile, World
from reverie.backend_server.world.world_objects.WorldObject import WorldObject

class SpatialMemory:
  def __init__(self, spatial_memory:dict, environment:World) -> None:
    try:
      self.__current_location:Tile = spatial_memory['current_location']
      self.__environment = environment
      self.__object_locations:dict[WorldObject,Tile] = spatial_memory['object_locations']
      self.__agent_locations:dict[Agent,Tile] = spatial_memory['agent']
    except:
      raise ValueError("Dictionary does not contain expected value")
    raise NotImplementedError()

  def process_visual_input(self,surrounding_environment:list[Tile])->list[str]:
    events_in_observable_environment:list[Tuple[float,str]] = []
    for tile in surrounding_environment:
      game_objects = tile.objects
      agents = tile.agents
      events = tile.events

      # arena's act as walls or availible fields of view. Its not perfect but its good enough
      if self.__current_location.is_in_same_arena(tile):
        for game_object in game_objects:
          self.__object_locations[game_object] = tile
        for agent in agents:
          self.__agent_locations[agent] = tile
        # This calculates the distance between the persona's current tile, 
        # and the target tile.
        dist = math.dist([tile.x, tile.x], 
                         [self.__current_location.x, 
                          self.__current_location.y])
        # Add any relevant events to our temp set/list with the distant info. 
        for event in events:
          if (dist,event) not in events_in_observable_environment: events_in_observable_environment.append((dist, event)) # the closest events are "processed first" by the brain
    # TODO, maybe this should be based on whats important instead of just the distance
    events_in_observable_environment.sort(key=lambda pair: pair[0])
    return [event for _,event in events_in_observable_environment]


  @property
  def current_location(self):
    return self.__current_location

  def get_known_objects(self):
    return [obj for obj in self.__object_locations.keys()]

  def get_known_people(self):
    return [agent for agent in self.__agent_locations.keys()]
