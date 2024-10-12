from datetime import datetime
from typing import Callable, Dict, Tuple
from reverie.backend_server.persona.core.Concept import Concept
from reverie.backend_server.persona.core.Memory import Memory
from reverie.backend_server.persona.core.Personality import Personality
from reverie.backend_server.persona.core.social.EmotionRegulator import EmotionalRegulator

from numba import njit
import numpy as np


class ShortTermMemory(Memory):
  def __init__(self,
               short_term:dict,
               time_func:Callable[[],datetime],
               emotion_regulator:EmotionalRegulator,
               personality:Personality
               ) -> None:
    try:
      concepts = short_term['concepts']
      super().__init__(concepts,emotion_regulator,time_func)
      self.__currently = short_term['currently']
      self.__attention_span = int(short_term['attention_span'])
      # used in reactions and for filtering
      self.__personality = personality

      # Current action

    except KeyError as e:
      raise ValueError(f"Dictionary does not contain expected keys:\n {e}")
    except TypeError as e:
      raise ValueError(f"Dictionary does not contain correct type:\n {e}")

  def process_events(self,new_events:list[str]):
    to_return:list[Concept] = []
    recent_events = [event.description for event in self._seq_event]
    for desc in new_events:
      # If the event is related to ourselves, it is assumed to already be registered
      #   In the event that hypothetically you would want to play out a scenario where
      #   an agent attacks another agent, then the status of the threat actor must
      #   not contain the name of the agent they are targeting until the other agent
      #   is aware of the attack happening.
      #   This behavior of the status should happen implicitly, but if you consistently.
      #   into problems, raise an issue on github and link your fork in the issue.
      if self.__personality.full_name.lower() in desc.lower():
        raise NotImplementedError()

      # We need to do something to describe more similar events.
      if desc in recent_events:
        #TODO: update the most recently accessed?
        # Seeing the same thing twice can hold value.
        raise NotImplementedError()
      # TODO: We should see if there are similar concepts to the thing
      #   we saw (something we see reminds us of something else).
      to_return.append(self._add_conceptnode(
          "event",
          self.get_current_time(),
          desc,
          [],
          ))
      # TODO: review how importance triggers work because its not clear yet how this is relevant and if i want to keep or initialize them here like in the initial code
      # TODO: return embeddings so that we can pass on to long term memory and refresh
      #   Those memories if there are any relevant memories.
      raise NotImplementedError()

    return to_return
    

  def _retrieval_score(self, concept: np.ndarray, potential_candidate: Concept) -> Tuple[float,...]:
    @njit
    def last_accessed_decay_function(x)->float:
        return 1.1 ** (-4 * x ** 2)

    @njit
    def importance_gradient_function(x)->float:
        return 0.5 * (np.exp(0.85 * (x - 1)) - np.exp(0.4 * (x - 1))) / (np.exp(0.8 * (x - 1)) + np.exp(-0.2 * (x - 1))) + 0.2

    last_accessed = potential_candidate.last_accessed
    current_time = self.get_current_time()
    # conversion to days
    time_delta = (current_time - last_accessed).total_seconds()/86400
    return (last_accessed_decay_function(time_delta),
            importance_gradient_function(potential_candidate.impact),
            self.__similarity_score_function(concept,potential_candidate.embedding))
  
  def retrieve_relevant_concepts(self, concepts: list[np.ndarray]) -> list[Concept]:
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
