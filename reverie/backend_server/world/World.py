"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: maze.py
Description: Defines the Maze class, which represents the map of the simulated
world in a 2-dimensional matrix. 
"""
from collections.abc import Callable
import json
from typing import Tuple
import numpy
import datetime
import pickle
import time
import math

from global_methods import *
from reverie.backend_server.world.world_objects.ObjectList import object_classes
from utils import *


# the third parameter must be a tile, the reason it is not is because of defintions
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
               objects:dict[str,Tuple[str,dict]],
               ) -> None:
    self.__sector = sector
    self.__arena = arena
    self.__x, self.__y = location
    self.objects = []
    for object_id,(object_name,object_data) in objects.items():
      if object_id in object_classes:
        self.objects.append(object_classes[object_id](object_id,object_name,object_data))
    # self.__objects = 
    pass

class World: 
  def __init__(self, maze_name): 
    # READING IN THE BASIC META INFORMATION ABOUT THE MAP
    self.maze_name = maze_name
    # Reading in the meta information about the world. If you want tp see the
    # example variables, check out the maze_meta_info.json file. 
    with json.load(open(f"{env_matrix}/maze_meta_info.json")) as meta_info:
      # <maze_width> and <maze_height> denote the number of tiles make up the 
        # height and width of the map. 
      self.maze_width = int(meta_info["maze_width"])
      self.maze_height = int(meta_info["maze_height"])
        # <sq_tile_size> denotes the pixel height/width of a tile. 
      self.sq_tile_size = int(meta_info["sq_tile_size"])
        # <special_constraint> is a string description of any relevant special 
        # constraints the world might have. 
        # e.g., "planning to stay at home all day and never go out of her home"
      self.special_constraint = meta_info["special_constraint"]

    # READING IN SPECIAL BLOCKS
    # Special blocks are those that are colored in the Tiled map. 

    # Here is an example row for the arena block file: 
    # e.g., "25335, Double Studio, Studio, Common Room"
    # And here is another example row for the game object block file: 
    # e.g, "25331, Double Studio, Studio, Bedroom 2, Painting"

    # Notice that the first element here is the color marker digit from the 
    # Tiled export. Then we basically have the block path: 
    # World, Sector, Arena, Game Object -- again, these paths need to be 
    # unique within an instance of Reverie. 

    # Revision Comments:
    # Reads in a bunch of specific world objects, in the format of a ID
    # as a key and a human readiable identifies as the value in a dictionary

    # Keeping id's as strings
    def csv_to_list(location:str)->list:
      with open(location,"r") as file:
        to_return = []
        for line in file:
          to_return.append(line.strip().split(','))
        return to_return

    blocks_folder = f"{env_matrix}/special_blocks"

    # getting only the id? this is what i think happened in the original code
    wb = csv_to_list(f"{blocks_folder}/world_blocks.csv")[-1]
   
    sb_rows = csv_to_list(f"{blocks_folder}/sector_blocks.csv")
    sb_dict = dict()
    for i in sb_rows: sb_dict[i[0]] = i[-1] 
    
    ab_rows = csv_to_list(f"{blocks_folder}/arena_blocks.csv")
    ab_dict = dict()
    for i in ab_rows: ab_dict[i[0]] = i[-1]
    
    gob_rows = csv_to_list(f"{blocks_folder}/game_object_blocks.csv")
    gob_dict = dict()
    for i in gob_rows: gob_dict[i[0]] = i[-1]
    
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

    # Revision Comments:
    # This defines the main object that we use to interact with the world?
    # it is a 2D array that indexes into a dictionary, the dictionary is of the form:
    # tiles[row][col] = {
    #           "world" : "world name",
    #           "sector" : "sector name",
    #           "arena" : "more detailed general position within sector",
    #           "game_object" : "object",
    #           "spawning_location" : "a spawn location identifier?",
    #           "collision" : boolean: indicates if position is accessable,
    #           "events" : numpy.set: a set of event tuples, 
    #                       first item: is a identy specified by the rest of the tiles 
    #                           properties which is odd? because its redundant.
    #                       and then defaults to another 3 paramters of type None]
    #       }
    self.tiles = []
    for i in range(self.maze_height): 
      row = []
      for j in range(self.maze_width):
        tile_details = dict()
        tile_details["world"] = wb
        
        tile_details["sector"] = ""
        if sector_maze[i][j] in sb_dict: 
          tile_details["sector"] = sb_dict[sector_maze[i][j]]
        
        tile_details["arena"] = ""
        if arena_maze[i][j] in ab_dict: 
          tile_details["arena"] = ab_dict[arena_maze[i][j]]
        
        tile_details["game_object"] = ""
        if game_object_maze[i][j] in gob_dict: 
          tile_details["game_object"] = gob_dict[game_object_maze[i][j]]
        
        tile_details["spawning_location"] = ""
        if spawning_location_maze[i][j] in slb_dict: 
          tile_details["spawning_location"] = slb_dict[spawning_location_maze[i][j]]
        
        tile_details["collision"] = False
        if collision_maze[i][j] != "0": 
          tile_details["collision"] = True

        tile_details["events"] = set()
        
        row += [tile_details]
      self.tiles += [row]
    # Each game object occupies an event in the tile. We are setting up the 
    # default event value here. 
    for i in range(self.maze_height):
      for j in range(self.maze_width): 
        if self.tiles[i][j]["game_object"]:
          object_name = ":".join([self.tiles[i][j]["world"], 
                                  self.tiles[i][j]["sector"], 
                                  self.tiles[i][j]["arena"], 
                                  self.tiles[i][j]["game_object"]])
          go_event = (object_name, None, None, None)
          self.tiles[i][j]["events"].add(go_event)

    # Reverse tile access. 
    # <self.address_tiles> -- given a string address, we return a set of all 
    # tile coordinates belonging to that address (this is opposite of  
    # self.tiles that give you the string address given a coordinate). This is
    # an optimization component for finding paths for the personas' movement. 
    # self.address_tiles['<spawn_loc>bedroom-2-a'] == {(58, 9)}
    # self.address_tiles['double studio:recreation:pool table'] 
    #   == {(29, 14), (31, 11), (30, 14), (32, 11), ...}, 

    # Review Notes:
    # This is cool, rewritten to be more pythonic
    self.address_tiles = dict()
    for i in range(self.maze_height):
      for j in range(self.maze_width): 
        addresses = []
        if self.tiles[i][j]["sector"]: 
          addresses.append(":".join([
            f'{self.tiles[i][j]["world"]}',
            f'{self.tiles[i][j]["sector"]}'
            ]))
        if self.tiles[i][j]["arena"]: 
          addresses.append(":".join([
            f'{self.tiles[i][j]["world"]}',
            f'{self.tiles[i][j]["sector"]}',
            f'{self.tiles[i][j]["arena"]}'
            ]))
        if self.tiles[i][j]["game_object"]: 
          addresses.append(":".join([
            f'{self.tiles[i][j]["world"]}',
            f'{self.tiles[i][j]["sector"]}',
            f'{self.tiles[i][j]["arena"]}',
            f'{self.tiles[i][j]["game_object"]}'
            ]))
        if self.tiles[i][j]["spawning_location"]: 
          addresses.append(f'<spawn_loc>{self.tiles[i][j]["spawning_location"]}')

        for add in addresses: 
          if add in self.address_tiles: 
            self.address_tiles[add].add((j, i))
          else: 
            self.address_tiles[add] = set([(j, i)])


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
  def access_tile(self, tile): 
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
    x = tile[0]
    y = tile[1]
    return self.tiles[y][x]


  def get_tile_path(self, tile, level): 
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
    x = tile[0]
    y = tile[1]
    tile = self.tiles[y][x]

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


  # Review Note:
  # TODO rename to get_nearby_tile_coordinates for clarity and consistency
  def get_nearby_tiles(self, tile, vision_r):
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
    left_end = 0
    if tile[0] - vision_r > left_end: 
      left_end = tile[0] - vision_r

    right_end = self.maze_width - 1
    if tile[0] + vision_r + 1 < right_end: 
      right_end = tile[0] + vision_r + 1

    bottom_end = self.maze_height - 1
    if tile[1] + vision_r + 1 < bottom_end: 
      bottom_end = tile[1] + vision_r + 1

    top_end = 0
    if tile[1] - vision_r > top_end: 
      top_end = tile[1] - vision_r 

    nearby_tiles = []
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

  def add_event_from_tile(self, curr_event, tile): 
    """
    Add an event triple to a tile.  

    INPUT: 
      curr_event: Current event triple. 
        e.g., ('double studio:double studio:bedroom 2:bed', None,
                None)
      tile: The tile coordinate of our interest in (x, y) form.
    OUPUT: 
      None
    """
    self.tiles[tile[1]][tile[0]]["events"].add(curr_event)


  def remove_event_from_tile(self, curr_event, tile):
    """
    Remove an event triple from a tile.  

    INPUT: 
      curr_event: Current event triple. 
        e.g., ('double studio:double studio:bedroom 2:bed', None,
                None)
      tile: The tile coordinate of our interest in (x, y) form.
    OUPUT: 
      None
    """
    curr_tile_ev_cp = self.tiles[tile[1]][tile[0]]["events"].copy()
    for event in curr_tile_ev_cp: 
      if event == curr_event:  
        self.tiles[tile[1]][tile[0]]["events"].remove(event)


  def turn_event_from_tile_idle(self, curr_event, tile):
    curr_tile_ev_cp = self.tiles[tile[1]][tile[0]]["events"].copy()
    for event in curr_tile_ev_cp: 
      if event == curr_event:  
        self.tiles[tile[1]][tile[0]]["events"].remove(event)
        new_event = (event[0], None, None, None)
        self.tiles[tile[1]][tile[0]]["events"].add(new_event)


  def remove_subject_events_from_tile(self, subject, tile):
    """
    Remove an event triple that has the input subject from a tile. 

    INPUT: 
      subject: "Isabella Rodriguez"
      tile: The tile coordinate of our interest in (x, y) form.
    OUPUT: 
      None
    """
    curr_tile_ev_cp = self.tiles[tile[1]][tile[0]]["events"].copy()
    for event in curr_tile_ev_cp: 
      if event[0] == subject:  
        self.tiles[tile[1]][tile[0]]["events"].remove(event)

































