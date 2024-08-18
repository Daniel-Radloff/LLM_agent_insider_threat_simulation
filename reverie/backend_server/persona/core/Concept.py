class Concept: 
  def __init__(self,
               node_id, node_count, type_count, node_type, depth,
               created, expiration, 
               s, p, o, 
               description, embedding_key, poignancy, keywords, chat_history): 
    self.id = node_id
    self.count = node_count
    self.type_count = type_count
    self.type_of_concept = node_type # thought / event / chat
    self.depth = depth

    self.created = created
    self.expiration = expiration
    self.last_accessed = self.created

    self.concept_subject = s
    self.concept_predicate = p
    self.concept_object = o

    self.description = description
    self.embedding_key = embedding_key
    self.poignancy = poignancy
    self.keywords = keywords
    # TODO: refactor into a chat node or something because this is stupid
    self.chat_history = chat_history

  def __eq__(self, value: object, /) -> bool:
    if isinstance(value, Concept):
      this_tuple = (self.concept_subject, self.concept_predicate, self.concept_object, self.description)
      other_tuple = (value.concept_subject, value.concept_predicate, value.concept_object, value.description)
      if value.created == self.created and this_tuple == other_tuple:
        return True
    return False

  def spo_summary(self): 
    return (self.concept_subject, self.concept_predicate, self.concept_object)
