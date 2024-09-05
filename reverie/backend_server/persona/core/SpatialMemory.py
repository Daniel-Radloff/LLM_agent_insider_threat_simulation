'''
In the original code, spatial memory existed as a way to tie events to the game world.
With an object oriented approach, a colegue has suggested that I do away with this
in favor for conceptualizing the entire world and all information about it within the
Concept objects.
For now, this class will remain just to get the project to a workable state.
'''
from typing import List, Tuple

import numpy as np
from numpy.lib import math
from reverie.backend_server.persona.Agent import Agent
from reverie.backend_server.world.World import Tile, World
from reverie.backend_server.world.world_objects.WorldObject import WorldObject

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

class SpatialMemory:
  def __init__(self, spatial_memory:dict, environment:World) -> None:
    try:
      self.__current_location:Tile = spatial_memory['current_location']
      self.__environment = environment
      self.__object_locations:dict[WorldObject,Tile] = spatial_memory['object_locations']
      self.__agent_locations:dict[str,Tile] = spatial_memory['agent']
      self.__current_path:List[Tile] = []
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
          self.__agent_locations[agent.name] = tile
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


  def _path_finding(self,target:Tile):
    collision_maze = Grid(matrix=self.__environment.collision_map.tolist())
    current_position = collision_maze.node(
        self.__current_location.x, 
        self.__current_location.y)
    target_position = collision_maze.node(target.x, target.y)
    # optimal movement, we should probably make it more 
    # inefficient some how to make the movements more human, 
    # or just design the map in a way that its more human
    a_star = AStarFinder(diagonal_movement=DiagonalMovement.always)
    path,_ = a_star.find_path(current_position,target_position,collision_maze)
    path_co_ordinates:list[tuple[int,int]] = [(node.x,node.y) for node in path]
    path_co_ordinates.reverse()
    self.__current_path = []
    for tile in path_co_ordinates:
      self.__current_path.append(self.__environment.get_tile(tile))

  def get_next_step(self)->Tile|None:
    if self.__current_path == []:
      return None
    else:
      return self.__current_path.pop()

  @property
  def current_location(self):
    return self.__current_location

  def get_known_objects(self):
    return [(obj,(location.x,location.y))for obj,location in self.__object_locations.items()]

  def get_known_people(self):
    return [(agent,(location.x,location.y)) for agent,location in self.__agent_locations.items()]

  def get_distance_from_position(self,):

