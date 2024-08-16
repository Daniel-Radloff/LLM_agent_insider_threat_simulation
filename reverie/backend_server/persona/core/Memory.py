from abc import ABC
from datetime import datetime 
from typing import Callable, Dict, Tuple, Union

from reverie.backend_server.persona.core.Concept import Concept


class Memory(ABC):
  def __init__(self,
               embeddings:Dict[str,list[float]], 
               concepts:dict,
               keyword_strengths:dict,
               current_time_func:Callable[[],datetime]
               ) -> None:
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

      # For those unfamiliar, see https://datasciencedojo.com/blog/embeddings-and-llm/ or any
      # other resource on embeddings related to LLM's
      # Any embedding model can be used, all that is important is that the same model is used.
      # These are supposed to be in a with for robustness, but im not going to do that because
      # I don't wanna edit this file anymore so this is now TODO
      self._embeddings = embeddings
      # Makes all the event nodes
      for _,concept in concepts:
        node_type = concept["type"]

        created = datetime.strptime(concept["created"], 
                                             '%Y-%m-%d %H:%M:%S')
        if concept["expiration"]: 
          expiration = datetime.strptime(concept["expiration"],
                                                  '%Y-%m-%d %H:%M:%S')
        else:
          expiration = None

        s = concept["subject"]
        p = concept["predicate"]
        o = concept["object"]

        description = concept["description"]
        embedding_pair = (concept["embedding_key"], 
                          self._embeddings[concept["embedding_key"]])
        poignancy =concept["poignancy"]
        keywords = set(concept["keywords"])
        filling = concept["filling"]
        
        self._add_conceptnode(created, expiration, s, p, o, 
                   description, keywords, poignancy, embedding_pair, filling,node_type)

      # Review Note:
      # Can't tell right now if this is used outside of this class, which would be weird.
      # Refactoring should reveal more.
      if keyword_strengths["kw_strength_event"]: 
        self._kw_strength_event = keyword_strengths["kw_strength_event"]
      if keyword_strengths["kw_strength_chat"]: 
        self._kw_strength_chat = keyword_strengths["kw_strength_chat"]
      if keyword_strengths["kw_strength_thought"]: 
        self._kw_strength_thought = keyword_strengths["kw_strength_thought"]
    except:
      raise ValueError("Dictionary does not contain expect value")
    self.__time_func = current_time_func

  def _add_conceptnode(self, 
                       created:datetime,
                       expiration:Union[datetime,None],
                       s:str,
                       p:str,
                       o:str, 
                       description:str, 
                       keywords:list[str], 
                       poignancy:int, 
                       embedding_pair:Tuple[str,list[float]],
                       filling, node_type:str)->Concept:
    # For this refactor, we use getattr a lot because its convenient
    # All it does is access a attribute.
    # So: self.kw_strength_event
    # can be accessed using: getattr(self, "kw_strength_event")
    # this is convienient cause we can use strings to access 
    # different keywords

    # Little idle check function
    def is_idle_check():
      kw_strength_list:dict = getattr(self, f"kw_strength_{node_type}")
      if f"{p} {o}" != "is idle":  
        for kw in keywords: 
          if kw in kw_strength_list: 
            kw_strength_list[kw] += 1
          else: 
            kw_strength_list[kw] = 1

    depth = 0
    # Node type specific operations
    if node_type == "chat":
      # TODO, maybe change this because of refactor
      check_idle = lambda : None
    elif node_type == "event":
      # Event node specific clean up. 
      check_idle = is_idle_check
      if "(" in description: 
        description = (" ".join(description.split()[:3]) 
                       + " " 
                       +  description.split("(")[-1][:-1])
    elif node_type == "thought":
      depth = 1 
      check_idle = is_idle_check
      try: 
        if filling: 
          depth += max([self._id_to_node[i].depth for i in filling])
      except: 
        pass
    else:
      raise NotImplementedError("Invalid node_type")

    # Setting up the node ID and counts.
    node_count = len(self._id_to_node.keys()) + 1
    type_count = len(getattr(self,f"seq_{node_type}")) + 1 
    node_id = f"node_{str(node_count)}"

    # Creating the <ConceptNode> object.
    node = Concept(node_id, node_count, type_count, node_type, depth,
                       created, expiration, 
                       s, p, o, 
                       description, embedding_pair[0], 
                       poignancy, keywords, filling)

    # Creating various dictionary cache for fast access. 
    # Review Note:
    # its an insert because the items closest to the start are assumed to be the items most recently added

    getattr(self, f"seq_{node_type}").insert(0,node)
    keywords = [i.lower() for i in keywords]
    for kw in keywords: 
      kw_list = getattr(self, f"kw_to_{node_type}")
      if kw in kw_list:
        kw_list[kw].insert(0,node)
      else: 
        kw_list[kw] = [node]
    self._id_to_node[node_id] = node 

    check_idle()
    self._embeddings[embedding_pair[0]] = embedding_pair[1]

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
    def try_remove_from_keywords(target_node:Concept,keywords:Dict[str,list],keyword_strenghts:dict):
      for keyword,concepts in keywords.items():
        try:
          concepts.remove(target_node)
          # surely?
          keyword_strenghts[keyword] -= 1
        # for the list removal
        except ValueError:
          pass
        # for the index into the keyword_strengths dict
        except KeyError:
          raise RuntimeError("A keyword is not defined in the keyword strength list")


    node = self._id_to_node.pop(node_id,None)
    if node == None:
      raise ValueError(f"Node with provided ID: '{node_id}' does not exist")

    try_remove_list(node,self._seq_event)
    try_remove_list(node,self._seq_thought)
    try_remove_list(node,self._seq_chat)

    try_remove_from_keywords(node, self._kw_to_event, self._kw_strength_event)
    try_remove_from_keywords(node, self._kw_to_thought, self._kw_strength_thought)
    try_remove_from_keywords(node, self._kw_to_chat, self._kw_strength_chat)

  # Placeholder TODO
  # Will do embedding call here for now without the model thing, bad practice might TODO and fix later but for now its good enough.
  def _generate_embedding(self, phrase:str)->list[float]:
    pass
    return[]

  def _get_current_time(self):
    self.__time_func()
