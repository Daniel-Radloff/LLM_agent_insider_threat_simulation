class LongTermMemory:
  def __init__(self, long_term_memory:dict) -> None:
    try: 
      self.learned_traits:str = long_term_memory['learned_traits']
    except:
      raise ValueError("Dictionary does not contain expect value")

  def get_learned_traits(self):
    return self.learned_traits
