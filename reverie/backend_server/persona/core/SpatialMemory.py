from typing import Tuple
from reverie.backend_server.maze import Maze


class SpatialMemory:
  def __init__(self, spatial_memory:dict) -> None:
    try:
      self.__current_location:Tuple[int,int] = spatial_memory['curr_tile']
      if len(self.current_location) != 2:
        raise ValueError("Current location is supposed to be of lenght 2, an x y co-ordinate pair")
    except:
      raise ValueError("Dictionary does not contain expected value")

  @property
  def current_location(self):
    return self.__current_location
