class LongTermMemory:
  def __init__(self, long_term_memory:dict) -> None:
    self.learned_traits:str = long_term_memory['learned']

  def get_learned_traits(self):
    return self.learned_traits
