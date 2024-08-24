"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: maze.py
Description: Defines the Maze class, which represents the map of the simulated
world in a 2-dimensional matrix. 
"""

# TODO all the pathing is going to be cooked, so once it runs and breaks, fix it.
from collections.abc import Callable
import json
from typing import Any, Literal, Tuple, Union
import math

from global_methods import *
from reverie.backend_server.world.world_objects.ObjectList import object_classes
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
               objects:dict[str,dict],
               ) -> None:
    self.__sector = sector
    self.__arena = arena
    self.__x, self.__y = location
    self.__objects = []
    self.__colidable = collide
    # See world_objects/ObjectList.py for a better understanding of whats happening in this loop
    for object_id,object_data in objects.items():
      if object_id in object_classes:
        self.__objects.append(object_classes[object_id](object_id,object_data))
      else:
        self.__objects.append(object_classes['default'](object_id,object_data))
    self.__agents:list[Agent]
    # TODO see if we can store agents in the tiles, but I suspect there will be a circular dependency

class World: 
  def __init__(self, maze_name): 
    self.maze_name = maze_name
    with json.load(open(f"{env_matrix}/maze_meta_info.json")) as meta_info:
      self.maze_width = int(meta_info["maze_width"])
      self.maze_height = int(meta_info["maze_height"])
        # <sq_tile_size> denotes the pixel height/width of a tile. 
      self.sq_tile_size = int(meta_info["sq_tile_size"])


    def csv_to_list(location:str)->list[list[str]]:
      with open(location,"r") as file:
        to_return = []
        for line in file:
          to_return.append(line.strip().split(','))
        return to_return

    # Revision Comments:
    # Reads in a bunch of specific world objects, in the format of a ID
    # as a key and a human readiable identifies as the value in a dictionary
    blocks_folder = f"{env_matrix}/special_blocks"

    sb_rows = csv_to_list(f"{blocks_folder}/sector_blocks.csv")
    sb_dict = dict()
    for i in sb_rows: sb_dict[i[0]] = i[-1] 
    
    ab_rows = csv_to_list(f"{blocks_folder}/arena_blocks.csv")
    ab_dict = dict()
    for i in ab_rows: ab_dict[i[0]] = i[-1]
    
    game_object_directory = f"{blocks_folder}/game_object_blocks"

    # Game objects can have unique data that they contain.
    gob_dict:dict[str,dict[str,Any]] = dict()
    for filename in os.listdir(game_object_directory):
      # sgo = simulation game object
      if filename.endswith('.sgo.json'):
        file_path = os.path.join(game_object_directory, filename)
        with open(file_path, 'r') as json_file:
          # TODO we should be doing more validation here to make sure the id's are unique 
          #   and that the id in the file matches the id of the file name etc.
          gob_dict[filename.split('.')[0]] = json.load(json_file)

    slb_rows = csv_to_list(f"{blocks_folder}/spawning_location_blocks.csv")
    slb_dict = dict()
    for i in slb_rows: slb_dict[i[0]] = i[-1]

    # Revision Comments:
    # The world is represented as a big 2D array, 
    # if its a 0, then 
    #   there is nothing in the way,
    # else
    #   it is a id that maps to a previously defined special object? 
    # a default collision block is defined in utils.py.
    maze_folder = f"{env_matrix}/maze"
    collision_maze = csv_to_list(f"{maze_folder}/collision_maze.csv")
    sector_maze = csv_to_list(f"{maze_folder}/sector_maze.csv")
    arena_maze = csv_to_list(f"{maze_folder}/arena_maze.csv")
    game_object_maze = csv_to_list(f"{maze_folder}/game_object_maze.csv")
    spawning_location_maze = csv_to_list(f"{maze_folder}/spawning_location_maze.csv")

    self.tiles:list[list[Tile]] = []
    for i in range(self.maze_height): 
      row:list[Tile] = []
      for j in range(self.maze_width):
        sector = sb_dict.get(sector_maze[i][j],"")
        arena = ab_dict.get(arena_maze[i][j],"")
        # TODO: Refactor game object maze so that multiple objects can be stored per tile
        # TODO: game_object_maze must have its id's validated before we assign, for now this will crash.
        game_object = gob_dict[game_object_maze[i][j]]
        spawning_location = slb_dict.get(spawning_location_maze[i][j],"")
        if collision_maze[i][j] == "0": 
          collide = False
        else:
          collide = True

        # Note: im keeping the tile orientation the same, 
        #   don't want to cause issues.
        tile = Tile(sector,arena,(i,j),collide,{game_object_maze[i][j] : game_object})

        # Note: Events used to be stored in the tile. Now: objects and agents should have a status, and the tile will emit those statuses as events.
        row += [tile]
      self.tiles += [row]

  # Review Notes:
  # Surely this is frontend related?
  def turn_coordinate_to_tile(self, px_coordinate): 
    """
    Turns a pixel coordinate to a tile coordinate. 

    INPUT
      px_coordinate: The pixel coordinate of our interest. Comes in the x, y
                     format. 
    OUTPUT
      tile coordinate (x, y): The tile coordinate that corresponds to the 
                              pixel coordinate. 
    EXAMPLE OUTPUT 
      Given (1600, 384), outputs (50, 12)
    """
    x = math.ceil(px_coordinate[0]/self.sq_tile_size)
    y = math.ceil(px_coordinate[1]/self.sq_tile_size)
    return (x, y)


  # Review Note:
  # TODO rename to get_tile_details for clarity and consistency
  def access_tile(self, tile:Tuple[int,int]): 
    """
    Returns the tiles details dictionary that is stored in self.tiles of the 
    designated x, y location. 

    INPUT
      tile: The tile coordinate of our interest in (x, y) form.
    OUTPUT
      The tile detail dictionary for the designated tile. 
    EXAMPLE OUTPUT
      Given (58, 9), 
      self.tiles[9][58] = {'world': 'double studio', 
            'sector': 'double studio', 'arena': 'bedroom 2', 
            'game_object': 'bed', 'spawning_location': 'bedroom-2-a', 
            'collision': False,
            'events': {('double studio:double studio:bedroom 2:bed',
                       None, None)}} 
    """
    row,col = tile
    return self.tiles[col][row]


  # Note:
  #   I don't know if im even going to use this, so I will leave it as broken for now
  def get_tile_path(self, location:Tuple[int,int], level:Literal["sector","arena"]):
    """
    Get the tile string address given its coordinate. You designate the level
    by giving it a string level description. 

    INPUT: 
      tile: The tile coordinate of our interest in (x, y) form.
      level: world, sector, arena, or game object
    OUTPUT
      The string address for the tile.
    EXAMPLE OUTPUT
      Given tile=(58, 9), and level=arena,
      "double studio:double studio:bedroom 2"
    """
    x,y = location
    tile = self.tiles[y][x]
    raise NotImplementedError()
    '''
    path = f"{tile['world']}"
    if level == "world": 
      return path
    else: 
      path += f":{tile['sector']}"
    
    if level == "sector": 
      return path
    else: 
      path += f":{tile['arena']}"

    if level == "arena": 
      return path
    else: 
      path += f":{tile['game_object']}"

    return path
    '''


  # Review Note:
  # TODO rename to get_nearby_tile_coordinates for clarity and consistency
  def get_nearby_tiles(self, center:Tuple[int,int], vision_r):
    """
    Given the current tile and vision_r, return a list of tiles that are 
    within the radius. Note that this implementation looks at a square 
    boundary when determining what is within the radius. 
    i.e., for vision_r, returns x's. 
    x x x x x 
    x x x x x
    x x P x x 
    x x x x x
    x x x x x

    INPUT: 
      tile: The tile coordinate of our interest in (x, y) form.
      vision_r: The radius of the persona's vision. 
    OUTPUT: 
      nearby_tiles: a list of tiles that are within the radius. 
    """
    row,col = center
    left_end = 0
    if row - vision_r > left_end: 
      left_end = row - vision_r

    right_end = self.maze_width - 1
    if row + vision_r + 1 < right_end: 
      right_end = row + vision_r + 1

    bottom_end = self.maze_height - 1
    if col + vision_r + 1 < bottom_end: 
      bottom_end = col + vision_r + 1

    top_end = 0
    if col - vision_r > top_end: 
      top_end = col - vision_r 

    nearby_tiles:list[Tuple[int,int]] = []
    for i in range(left_end, right_end): 
      for j in range(top_end, bottom_end): 
        nearby_tiles += [(i, j)]
    return nearby_tiles

  # This function will hopefully replace the get_nearby_tiles() function
  def get_surrounding_environment(self,
                                  tile:Tuple[int,int],
                                  vision_radius:int
                                  )->list[Tuple[dict,str,Tuple[int,int]]]:
    nearby_tiles = self.get_nearby_tiles(tile,vision_radius)
    to_return = []
    for tile in nearby_tiles:
      to_return.append((
        self.access_tile(tile),
        self.get_tile_path(tile,"arena"),
        tile
        ))
    return to_return
