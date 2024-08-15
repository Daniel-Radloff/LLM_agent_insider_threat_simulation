from typing import Dict
from reverie.backend_server.persona.core.Concept import Concept
from reverie.backend_server.persona.core.Memory import Memory


class ShortTermMemory(Memory):
  def __init__(self,
               short_term:dict[str,str],
               embeddings:Dict[str,list[float]], 
               concepts:dict, 
               keyword_strengths:dict) -> None:
    try:
      super().__init__(embeddings,concepts,keyword_strengths)
      self.__currently = short_term['currently']
      self.__attention_span = int(short_term['attention_span'])
    except KeyError as e:
      raise ValueError(f"Dictionary does not contain expected keys:\n {e}")
    except TypeError as e:
      raise ValueError(f"Dictionary does not contain correct type:\n {e}")

  def process_events(self):
    pass

  def cleanup(self):
    raise NotImplemented()

  @property
  def attention_span(self):
    return self.__attention_span
  @property
  def currently(self):
    return self.__currently
