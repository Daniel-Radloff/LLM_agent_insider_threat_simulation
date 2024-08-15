import datetime
from typing import Dict
from reverie.backend_server.persona.core.Concept import Concept
from reverie.backend_server.persona.core.Memory import Memory


class LongTermMemory(Memory):
  def __init__(self, 
               long_term_memory:dict, 
               embeddings:Dict[str,list[float]], 
               concepts:dict, 
               keyword_strengths:dict) -> None:
    try: 
      super().__init__(embeddings,concepts,keyword_strengths)
      self.__learned_traits:str = long_term_memory['learned_traits']
    except:
      raise ValueError("Dictionary does not contain expect value")

  @property
  def learned_traits(self):
    return self.__learned_traits
