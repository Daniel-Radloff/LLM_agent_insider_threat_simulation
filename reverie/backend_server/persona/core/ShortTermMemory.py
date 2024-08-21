from datetime import datetime
from typing import Callable, Dict, Tuple
from reverie.backend_server.persona.core.Concept import Concept
from reverie.backend_server.persona.core.Memory import Memory
from reverie.backend_server.persona.core.social.EmotionRegulator import EmotionalRegulator

from numba import njit
import numpy as np


class ShortTermMemory(Memory):
  def __init__(self,
               concepts:dict, 
               time_func:Callable[[],datetime],
               emotion_regulator:EmotionalRegulator,
               short_term:dict[str,str],
               ) -> None:
    try:
      super().__init__(concepts,emotion_regulator,time_func)
      self.__currently = short_term['currently']
      self.__attention_span = int(short_term['attention_span'])

      # Current action

    except KeyError as e:
      raise ValueError(f"Dictionary does not contain expected keys:\n {e}")
    except TypeError as e:
      raise ValueError(f"Dictionary does not contain correct type:\n {e}")

  def process_events(self,new_events:list):
    recent_events:list[Tuple[str,str,str]] = [event.spo_summary() for event in self._seq_event]
    for subject,proposition,obj,desc in new_events:
      if (subject,proposition,obj) in recent_events:
        #TODO update the most recently accessed? or maybe we still keep?
        # Seeing the same thing twice can hold sematic value.
        continue

      # IMPORTANT
      # The original method from congnitive_modules/observe.py: percieve(persona,maze)
      #   had a special case for if we encounter a event that is a chat with another agent.
      #   This case from what it looked like, assumed that our current action was a chat with someone.
      #   This refactor will assume that if we start a chat, we will register that concept in the
      #   Method where we start the chat, and therefor, the chat is already assumed to be in our 
      #   recent events and will thus be ignored.
      #   
      #   TODO: should we consider removing if we observe someone talkign to us? where the subject and object are basically switched?
      #   or is this case implicityly covered by how we register events, do two agents negotiate an agreed upon event name and register both
      #   their events with the same subject, proposition, and object?

      # TODO: redefine how events are put on the map so that we can differenciate between conversations.
      self._add_conceptnode(
          "event",
          self.get_current_time(),
          subject,
          proposition,
          obj,
          desc,
          [],
          )
      # TODO: review how importance triggers work because its not clear yet how this is relevant and if i want to keep or initialize them here like in the initial code

  def _retrieval_score(self, concept: Concept, potential_candidate: Concept) -> Tuple[float,...]:
    @njit
    def last_accessed_decay_function(x)->float:
        return 1.1 ** (-4 * x ** 2)

    @njit
    def importance_gradient_function(x)->float:
        return 0.5 * (np.exp(0.85 * (x - 1)) - np.exp(0.4 * (x - 1))) / (np.exp(0.8 * (x - 1)) + np.exp(-0.2 * (x - 1))) + 0.2

    last_accessed = potential_candidate.last_accessed
    current_time = self.get_current_time()
    time_delta = current_time - last_accessed
    return (last_accessed_decay_function(time_delta),
            importance_gradient_function(potential_candidate.impact),
            self.__similarity_score_function(concept.embedding,potential_candidate.embedding))
  
  def retrieve_relevant_concepts(self, concepts: list[Concept]) -> list[Concept]:
    # Factors: 
    # Weight 1, Last accessed: this is short term memory so we forget quicker
    return self._retrieve_relevant_concepts(concepts,(1,2,2))[:self.__attention_span]
  
  def cleanup(self):
    raise NotImplemented()

  @property
  def current_events(self):
    '''
    Returns all events that have happened right now
    '''
    return [concept for _, concept in self._id_to_node.items() if concept.created == self.get_current_time()]

  @property
  def attention_span(self):
    return self.__attention_span

  @property
  def currently(self):
    return self.__currently
