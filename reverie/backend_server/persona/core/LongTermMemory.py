from datetime import datetime
from typing import Callable, Dict
from reverie.backend_server.persona.core.Concept import Concept
from reverie.backend_server.persona.core.Memory import Memory
from reverie.backend_server.persona.models.model import Model


class LongTermMemory(Memory):
  def __init__(self, 
               long_term_memory:dict, 
               embeddings:Dict[str,list[float]], 
               concepts:dict, 
               keyword_strengths:dict,
               embedding_model:Model,
               time_func:Callable[[],datetime]
               ) -> None:
    try: 
      super().__init__(embeddings,concepts,keyword_strengths,time_func)
      self.__learned_traits:str = long_term_memory['learned_traits']
    except:
      raise ValueError("Dictionary does not contain expect value")

  @property
  def learned_traits(self):
    return self.__learned_traits
