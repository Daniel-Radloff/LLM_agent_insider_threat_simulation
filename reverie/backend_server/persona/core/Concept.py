from datetime import datetime
from typing import Literal
import numpy as np


class Concept: 
  def __init__(self,
               node_id:str,
               node_type:Literal["chat","event","thought"],
               created:datetime, 
               s:str, p:str, o:str,
               description:str, 
               embedding:np.ndarray,
               impact:int,
               chat_history): 
    self._id = node_id
    self._type_of_concept = node_type # thought / event / chat

    self._created = created
    self._last_accessed = self._created

    self._concept_subject = s
    self._concept_predicate = p
    self._concept_object = o

    self._description = description
    # Maybe change to just the embedding per concept?
    self._embedding = np.array(embedding)
    self._impact = impact
    #
    self._keywords = list(set([s.split(":")[-1].lower(),o.split(":")[-1].lower()]))

    # TODO: refactor into a chat node or something because this is stupid
    self._chat_history = chat_history

  def __eq__(self, value: object, /) -> bool:
    if isinstance(value, Concept):
      this_tuple = (self._concept_subject, self._concept_predicate, self._concept_object, self._description)
      other_tuple = (value._concept_subject, value._concept_predicate, value._concept_object, value._description)
      if value._created == self._created and this_tuple == other_tuple:
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

  def spo_summary(self): 
    return (self._concept_subject, self._concept_predicate, self._concept_object)

  @property
  def embedding(self):
    return self._embedding

  @property
  def impact(self):
    return self._impact

  @property
  def description(self):
    return self._description
