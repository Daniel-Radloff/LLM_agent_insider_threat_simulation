import json
from reverie.backend_server.world.World import Tile, World
from reverie.backend_server.world.world_objects.WorldObject import WorldObject
from reverie.backend_server.world.world_objects.ObjectList import object_class_initializers


class WorldFactory:

  def __init__(self) -> None:
    pass

  def produce_world(self,location:str)->World:
    '''
    Location should be a directory located under the world
    storage files that contains the files related to the world
    to load. Its best to call that directory the same name as the
    world.
    '''
    def load_map(location:str)->list[list[str]]:
      with open(location,"r") as file:
        to_return = []
        for line in file:
          to_return.append(line.strip().split(','))
      # TODO: idk if the width and length are swapped or not yet but this will catch that, i think i definitely made a mistake.
      if len(to_return) != map_width:
        raise ValueError(f"Map metadata miss matches defined map '{location}': meta data map width:{map_width}, real map width: {len(to_return)}")

      # Validate colluns
      for count,row in enumerate(to_return):
        if len(row) != map_length:
          raise ValueError(f"Map metadata miss matches defined map '{location}': meta data map length:{map_length}, real map width: {len(row)} on line {count + 1}")
      return to_return

    with json.load(open(f"{location}/world_meta_info.json",'r')) as meta_info:
      world_name = meta_info['name']
      map_length = int(meta_info["map_length"])
      map_width = int(meta_info["map_width"])

    blocks_folder = f"{location}/blocks"
    sector_info = json.load(open(f"{blocks_folder}/sectors.json",'r'))
    area_info = json.load(open(f"{blocks_folder}/arenas.json",'r'))
    game_object_info = json.load(open(f"{blocks_folder}/game_objects.json",'r'))

    # The world is represented as a big 2D array,
    #   Dimentions are validated in csv_to_list
    map_directory = f"{location}/maze"
    collision_map = load_map(f"{map_directory}/collision_maze.csv")
    sector_locations = load_map(f"{map_directory}/sector_maze.csv")
    arena_locations = load_map(f"{map_directory}/arena_maze.csv")
    # Every game object, even if it is of the same type has a unique ID
    game_object_locations = load_map(f"{map_directory}/game_object_maze.csv")

    # Create game objects
    game_objects = self.__create_game_objects(game_object_info)

    # Create tiles array
    tiles:list[list[Tile]] = []
    for x in range(map_width):
      row:list[Tile] = []
      for y in range(map_length):
        sector = sector_info.get(sector_locations[x][y],"")
        arena = area_info.get(arena_locations[x][y],"")
        # TODO: Refactor game object maze so that multiple objects can be stored per tile
        # TODO: game_object_maze must have its id's validated before we assign, for now this will crash.
        game_object = game_objects[game_object_locations[x][y]]
        if collision_map[x][y] == "0": 
          collide = False
        else:
          collide = True

        # Note: im keeping the tile orientation the same, 
        #   don't want to cause issues.
        tile = Tile(sector,arena,(x,y),collide,[game_object])

        # Note: Events used to be stored in the tile. Now: objects and agents should have a status, and the tile will emit those statuses as events.
        row.append(tile)
      tiles.append(row)

    # Create world
    return World(world_name,map_width,map_length,tiles)

  def __create_game_objects(self,game_object_info:dict[str,dict])->dict[str,WorldObject]:
    to_return:dict = {}
    for id,game_object in game_object_info.items():
      if game_object['type_id'] in object_class_initializers:
        to_return[id] = object_class_initializers[game_object['type_id']](id,game_object)
      else:
        to_return[id] = object_class_initializers[game_object['default']](id,game_object)
    return to_return
