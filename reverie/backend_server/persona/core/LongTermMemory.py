from datetime import datetime
from typing import Callable, Dict
from reverie.backend_server.persona.core.Concept import Concept
from reverie.backend_server.persona.core.Memory import Memory
from reverie.backend_server.persona.core.social.EmotionRegulator import EmotionalRegulator
from reverie.backend_server.persona.models.model import Model


class LongTermMemory(Memory):
  def __init__(self, 
               concepts:dict, 
               emotion_regulator:EmotionalRegulator,
               time_func:Callable[[],datetime],
               long_term_memory:dict
               ) -> None:
    try: 
      super().__init__(concepts,emotion_regulator,time_func)
      self.__learned_traits:str = long_term_memory['learned_traits']
    except:
      raise ValueError("Dictionary does not contain expect value")

  @property
  def learned_traits(self):
    return self.__learned_traits
