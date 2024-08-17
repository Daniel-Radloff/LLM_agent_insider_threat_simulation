from datetime import datetime
from typing import Callable, Dict, Tuple
from reverie.backend_server.persona.core.Concept import Concept
from reverie.backend_server.persona.core.Memory import Memory
from reverie.backend_server.persona.core.social.EmotionRegulator import EmotionalRegulator


class ShortTermMemory(Memory):
  def __init__(self,
               short_term:dict[str,str],
               embeddings:Dict[str,list[float]], 
               concepts:dict, 
               keyword_strengths:dict,
               time_func:Callable[[],datetime],
               emotion_regulator:EmotionalRegulator) -> None:
    try:
      super().__init__(embeddings,concepts,keyword_strengths,time_func)
      self.__emotions = emotion_regulator
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
        continue

      if desc in self._embeddings: 
        event_embedding = self._embeddings[desc]
      else: 
        event_embedding = self._generate_embedding(desc)
      event_embedding_pair = (desc, event_embedding)
      keywords = list(set([subject.split(":")[-1],obj.split(":")[-1]]))
      event_impact = self.__emotions.determine_emotional_impact("event",desc)

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
          self._get_current_time(),
          # TODO: change expiration
          None,
          subject,
          proposition,
          obj,
          desc,
          keywords,
          event_impact,
          event_embedding_pair,
          [],
          "event"
          )
      # TODO: review how importance triggers work because its not clear yet how this is relevant and if i want to keep or initialize them here

  def cleanup(self):
    raise NotImplemented()

  @property
  def attention_span(self):
    return self.__attention_span
  @property
  def currently(self):
    return self.__currently
