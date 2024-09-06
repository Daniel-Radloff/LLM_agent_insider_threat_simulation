"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: maze.py
Description: Defines the Maze class, which represents the map of the simulated
world in a 2-dimensional matrix. 
"""
import numpy as np

'''
Important:
  Currently, the way the World works is a bit wonky, x,y co-ordiantes are used for access 
  outside of the class like you would expect, but internally the x and y are switched.
  If you want to modify something or work within the World class for now: use the get_tile
  method instead of attempting to use the list directly.
  Soon, this will be refactored into expected behavior.
'''

# TODO all the pathing is going to be cooked, so once it runs and breaks, fix it.
from collections.abc import Callable
import json
from typing import Any, Literal, Self, Tuple, Union
import math
import itertools

from global_methods import *
from reverie.backend_server.world.world_objects.WorldObject import WorldObject
from utils import *
from reverie.backend_server.persona.Agent import Agent


class Tile:
  '''
  Takes in objects in the form of a dictionary:
  {
  "id" : ("name", {object_data})
  }
  This is a single space in the world.
  It contains:
  - infromation about the spaces location
  - events occuring in the space
  - any objects located in the space
  - any agents located in the space
  When an agent enters a tile, all objects in the tile are notified.
  This is so that an object can block an agents path (such as a door)
  '''
  def __init__(self,
               sector:str,
               arena:str,
               location:Tuple[int,int],
               collide:bool,
               objects:list[WorldObject],
               ) -> None:
    self.__sector = sector
    self.__arena = arena
    self.__x, self.__y = location
    self.__objects:list[WorldObject] = []
    self.__colidable = collide
    # See world_objects/ObjectList.py for a better understanding of whats happening in this loop
    self.__objects = objects
    self.__agents:list[Agent] = []
    # TODO see if we can store agents in the tiles, but I suspect there will be a circular dependency

  def is_in_same_arena(self,to_compare:Self):
    if self.__sector == to_compare.__sector:
      if self.__arena == to_compare.__arena:
        return True
    return False

  def _add_agent(self,agent:Agent):
    self.__agents.append(agent)

  def _remove_agent(self,agent:Agent):
    self.__agents.remove(agent)

  @property
  def sector(self):
    return self.__sector

  @property
  def arena(self):
    return self.__arena

  @property
  def objects(self):
    # for the uninitiated [:] is a way of cloning a list in python
    return self.__objects[:]

  @property
  def agents(self):
    return self.__agents[:]

  @property
  def x(self):
    return self.__x

  @property
  def y(self):
    return self.__y

  @property
  def events(self):
    '''
    All events occuring in the tile.
    '''
    to_return:list[str] = []
    for obj in self.__objects:
      to_return.append(obj.status)
    for agent in self.__agents:
      to_return.append(agent.status)

    return to_return

  @property
  def wall(self):
    return self.__colidable


class World: 
  def __init__(self, world_name:str,width:int,length:int,tiles:list[list[Tile]]):
    self._maze_name = world_name
    self._maze_length = length
    self._maze_width = width
    self.__tiles = tiles

  def get_tile(self, tile:Tuple[int,int]): 
    """
    Returns the tile stored in self.tiles according to an x, y location. 

    INPUT
      tile: The tile coordinate of our interest in (x, y) form.
    OUTPUT
      The tile at the specified location.
    """
    x,y = tile
    return self.__tiles[x][y]

  def get_surrounding_environment(self,
                                  center:Tuple[int,int],
                                  vision_radius:int):
    x,y = center
    min_x = 0
    if x - vision_radius > min_x: 
      min_x = x - vision_radius

    max_x = self._maze_width - 1
    if x + vision_radius + 1 < max_x: 
      max_x = x + vision_radius + 1

    min_y = 0
    if y - vision_radius > min_y: 
      min_y = y - vision_radius 

    max_y = self._maze_length - 1
    if y + vision_radius + 1 < max_y: 
      max_y = y + vision_radius + 1

    return list(itertools.chain.from_iterable(self.__tiles[min_x:max_x][min_y:max_y]))

  @property
  def dimentions(self):
    return (self._maze_width,self._maze_length)

  @property
  def collision_map(self):
    collision_map = np.ones(self.dimentions, dtype=np.int32)
    for x,row in enumerate(self.__tiles):
      for y,tile in enumerate(row):
        if tile.wall:
          collision_map[x][y] = 0
    return collision_map
