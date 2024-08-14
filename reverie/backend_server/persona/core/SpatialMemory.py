from typing import Tuple

from numpy.lib import math
from reverie.backend_server.maze import Maze

class SpatialMemory:
  def __init__(self, spatial_memory:dict, environment:Maze) -> None:
    try:
      self.__current_location:Tuple[int,int] = spatial_memory['current_location']
      self.__environment = environment
      self.__spatial_memory = spatial_memory['spatial_memory']
      if len(self.current_location) != 2:
        raise ValueError("Current location is supposed to be of lenght 2, an x y co-ordinate pair")
    except:
      raise ValueError("Dictionary does not contain expected value")

  def process_environment(self,
                          current_tile:str,
                          surrounding_environment:list[Tuple[dict,str,Tuple[int,int]]])->list[tuple]:
    events_in_observable_environment = []
    for tile_dict,tile_description,coordinates in surrounding_environment:
      world = tile_dict["world"]
      sector = tile_dict["sector"]
      arena = tile_dict["arena"]
      game_object = tile_dict["arena"]
      events = tile_dict["events"]

      if (world and world not in self.__spatial_memory): 
        self.__spatial_memory[world] = {}
      if (sector and sector not in self.__spatial_memory[world]): 
        self.__spatial_memory[world][sector] = {}
      if (arena and arena not in self.__spatial_memory[world][sector]): 
        self.__spatial_memory[world][sector][arena] = []
      if (game_object and game_object not in self.__spatial_memory[world][sector][arena]): 
        self.__spatial_memory[world][sector][arena].append(game_object)

      if (events and tile_description == current_tile):
        # This calculates the distance between the persona's current tile, 
        # and the target tile.
        dist = math.dist([coordinates[0], coordinates[1]], 
                         [self.__current_location[0], 
                          self.__current_location[1]])
        # Add any relevant events to our temp set/list with the distant info. 
        for event in events:
          if (dist,event) not in events_in_observable_environment: 
            events_in_observable_environment.append((dist, event))
    # the closest events are "processed first" by the brain
    # TODO, maybe this should be based on whats important instead of just the distance
    events_in_observable_environment.sort(key=lambda pair: pair[0])
    return [event for _,event in events_in_observable_environment]


  @property
  def current_location(self):
    return self.__current_location
