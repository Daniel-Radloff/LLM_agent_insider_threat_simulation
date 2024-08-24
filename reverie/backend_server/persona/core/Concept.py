from datetime import datetime
from typing import Literal
import numpy as np


class Concept: 
  def __init__(self,
               node_id:str,
               node_type:Literal["chat","event","thought"],
               created:datetime, 
               description:str, 
               embedding:np.ndarray,
               impact:int,
               chat_history): 
    self._id = node_id
    self._type_of_concept = node_type # thought / event / chat

    self._created = created
    self._last_accessed = self._created
    self._description = description
    # Maybe change to just the embedding per concept?
    self._embedding = np.array(embedding)
    self._impact = impact

    # TODO: refactor into a chat node or something because this is stupid
    self._chat_history = chat_history

    # TODO: determine how to handle keywords
    self._keywords = list(set())
    raise NotImplementedError()

  def __eq__(self, value: object, /) -> bool:
    if isinstance(value, Concept):
      if value._created == self._created and self._description == value._description:
        return True
    return False
  
  @property
  def keywords(self):
    return self._keywords

  @property
  def created(self):
    return self._created

  @property
  def id(self):
    return self._id

  @property
  def last_accessed(self):
    return self._last_accessed

  @property
  def description(self): 
    return self._description

  @property
  def embedding(self):
    return self._embedding

  @property
  def impact(self):
    return self._impact
