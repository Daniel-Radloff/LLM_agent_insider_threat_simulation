from abc import ABC, abstractmethod
from datetime import datetime 
from typing import Callable, Dict, Literal, Tuple, Union

from reverie.backend_server.persona.core.Concept import Concept
from reverie.backend_server.persona.core.social.EmotionRegulator import EmotionalRegulator

from numba import njit
import numpy as np


class Memory(ABC):
  def __init__(self,
               concepts:dict,
               emotion_regulator:EmotionalRegulator,
               current_time_func:Callable[[],datetime]) -> None:
    super().__init__()
    try:
      self._id_to_node:Dict[str,Concept] = dict()

      self._seq_event:list[Concept] = []
      self._seq_thought:list[Concept] = []
      self._seq_chat:list[Concept] = []

      self._kw_to_event:Dict[str,list[Concept]] = dict()
      self._kw_to_thought:Dict[str,list[Concept]] = dict()
      self._kw_to_chat:Dict[str,list[Concept]] = dict()

      self._kw_strength_event:Dict[str,int] = dict()
      self._kw_strength_thought:Dict[str,int] = dict()
      self._kw_strength_chat:Dict[str,int] = dict()
      self._emotions = emotion_regulator

      # For those unfamiliar, see https://datasciencedojo.com/blog/embeddings-and-llm/ or any
      # other resource on embeddings related to LLM's
      # Any embedding model can be used, all that is important is that the same model is used.
      # Makes all the event nodes
      for _,concept in concepts:
        node_type = concept["type"]
        created = datetime.strptime(concept["created"], 
                                             '%Y-%m-%d %H:%M:%S')

        description = concept["description"]
        embedding = concept["embedding"]
        impact = concept["poignancy"]
        previous_chats = concept["filling"]
        
        self._add_conceptnode(node_type,
                              created,
                              description,
                              impact,
                              previous_chats,
                              embedding=embedding)
    except:
      raise ValueError("Dictionary does not contain expect value")
    self.__time_func:Callable[[],datetime] = current_time_func

  def _add_conceptnode(self, 
                       node_type:Literal["chat","event","thought"],
                       created:datetime,
                       description:str, 
                       previous_chats,
                       impact:Union[None,int] = None,
                       embedding:Union[None,np.ndarray] = None)->Concept:
    # For this refactor, we use getattr a lot because its convenient
    # All it does is access a attribute.
    # So: self.kw_strength_event
    # can be accessed using: getattr(self, "kw_strength_event")
    # this is convienient cause we can use strings to access 
    # different keywords

    # Setting up the node ID and counts.
    node_count = len(self._id_to_node.keys()) + 1
    node_id = f"node_{str(node_count)}"
    if embedding == None:
      embedding = self._generate_embedding(description)
    if impact == None:
      impact = self._emotions.determine_emotional_impact(node_type,description)

    # Creating the <ConceptNode> object.
    node = Concept(node_id,
                   node_type,
                   created, 
                   description,
                   embedding, 
                   impact,
                   previous_chats)

    # Creating various dictionary cache for fast access. 
    # Review Note:
    # its an insert because the items closest to the start are assumed to be the items most recently added, but this is irrelevant because nodes are ranked on when last they were accessed, not when they were added.

    getattr(self, f"seq_{node_type}").insert(0,node)
    keywords = [i.lower() for i in node.keywords]
    for kw in keywords: 
      kw_list = getattr(self, f"kw_to_{node_type}")
      if kw in kw_list:
        kw_list[kw].insert(0,node)
      else: 
        kw_list[kw] = [node]
    self._id_to_node[node_id] = node 

    return node

  def _remove_node(self,node_id:str):
    '''
    Removes any node via ID, this checks all availible lists.
    Assumes ID's are unique.
    '''
    def try_remove_list(node:Concept,list_potentially_containing_item:list):
      try:
        list_potentially_containing_item.remove(node)
      except:
        pass
    def try_remove_from_keywords(target_node:Concept,keywords:Dict[str,list]):
      for _,concepts in keywords.items():
        try:
          concepts.remove(target_node)
        except ValueError:
          pass

    node = self._id_to_node.pop(node_id,None)
    if node == None:
      raise ValueError(f"Node with provided ID: '{node_id}' does not exist")

    try_remove_list(node,self._seq_event)
    try_remove_list(node,self._seq_thought)
    try_remove_list(node,self._seq_chat)

    try_remove_from_keywords(node, self._kw_to_event)
    try_remove_from_keywords(node, self._kw_to_thought)
    try_remove_from_keywords(node, self._kw_to_chat)

  # Placeholder TODO
  # Will do embedding call here for now without the model thing, bad practice might TODO and fix later but for now its good enough.
  def _generate_embedding(self, phrase:str)->np.ndarray:
    raise NotImplementedError()

  def get_current_time(self)->datetime:
    return self.__time_func()
  
  @abstractmethod
  def _retrieval_score(self,concept:np.ndarray, potential_candidate:Concept)->Tuple[float,...]:
    '''
    This function should determine how relevant a candidate concept
    is to the concept being evaluated.
    It must return a tuple of float values inbetween 0 and 1 (this is not checked but recommended).
    These values will be used in the _retrieve_relevant_concept_scores, and retrieve_relevant_concepts functions by multiplying them to weights and summing them to generate a relevance score for the concept.

    If the length of the returned tuple is not equal to the weights provided to
    retrieve_relevant_concepts, then _retrieve_relvant_concept_scores will raise a 
    RuntimeError.
    '''
    raise NotImplementedError(f"concrete class: {type(self)} must impliment abstract method: _retrieval_score. See core/Memory.py:_retrieval_score")

  def _retrieve_relevant_concept_scores(self,concept:np.ndarray,relevance_weights:tuple)->list[Tuple[float,Concept]]:
    '''
    Takes in a list of concepts and looks in memory for relevant concepts.
    Concepts are ranked by the _retrieval_score method which determines the likely hood
    of a concept being remembered
    _retrieval_score is a abstract method that must be implimented by the concrete class.
    '''
    # could be a list but better safe than sorry
    relevance_scores:list[Tuple[float,Concept]] = []
    for _, concept_candidate in self._id_to_node.items():
      if concept == concept_candidate.embedding:
        continue
      raw_score = self._retrieval_score(concept,concept_candidate)

      if len(raw_score) != len(relevance_weights):
        raise RuntimeError("Tuple returned by _retrieval_score, does not match the length of the weights used in calculating final score")

      # dot product of the tuples appended to the index corresponding with the node were
      # evaluating
      relevance_scores.append(
          (sum(x*y for x,y in zip(raw_score,relevance_weights)), 
           concept_candidate))
    return relevance_scores

  def _retrieve_relevant_concepts(self,concepts:list[np.ndarray],relevance_weights:tuple)->list[Concept]:
    '''
    Takes in a list of concepts and looks in memory for relevant concepts.
    Concepts are ranked by the _retrieval_score method which determines the likely hood
    of a concept being remembered
    _retrieval_fitler is a abstract method that must be implimented by the concrete class.
    '''
    relevance_scores:dict[str,Tuple[float,Concept]] = {}
    for concept in concepts:
      candidate_scores = self._retrieve_relevant_concept_scores(concept,relevance_weights)
      for candidate in candidate_scores:
        # Check if candidate has already been seen
        candidate_id = candidate[1].id
        if candidate_id in relevance_scores:
          #  update if the relevance score is greater than what was previously assigned to it.
          old_score = relevance_scores[candidate_id][0]
          if old_score < candidate[0]:
            # TODO, maybe scale because it came up a second time?
            relevance_scores[candidate_id] = candidate
        else:
          relevance_scores[candidate_id] = candidate

    to_return = sorted(relevance_scores.values(),key=lambda x:x[0],reverse=True)
    return [concept for _, concept in to_return]
  
  @abstractmethod
  def retrieve_relevant_concepts(self,concepts:list[np.ndarray])->list[Concept]:
    '''
    This function is a frontend for the _retrieve_relevant_concepts function.
    It should contain line a line that calls _retrieve_relevant_concepts with the default weights used in memory retrieval.

    Takes in a list of concepts and looks in memory for relevant concepts.
    Concepts are ranked by the _retrieval_score method which determines the likely hood
    of a concept being remembered
    _retrieval_fitler is a abstract method that must be implimented by the concrete class.
    '''
    raise NotImplementedError(f"concrete class: {type(self)} must impliment abstract method: retrieve_relevant_concepts. See core/Memory.py:retrieve_relevant_concepts")


  @njit
  def __similarity_score_function(self,a, b):
    '''
    This function can return a negative value, but the likely hood is
    very low after testing, and if a negative value does occur, then it means
    the embeddings must be so distant from each other that it is a good thing.
    '''
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

