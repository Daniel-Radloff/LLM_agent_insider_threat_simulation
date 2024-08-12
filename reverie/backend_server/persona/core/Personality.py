from reverie.backend_server.persona.core.LongTermMemory import LongTermMemory

class Personality:
  def __init__(self,
               personality:dict[str,str],
               long_term_memory:LongTermMemory) -> None:
    try:
      self.__first_name = personality['first_name']
      self.__last_name = personality['last_name']
      self.__age = int(personality['age'])
      self.__innate_traits = personality['innate_traits']
      self.__lifestyle = personality['lifestyle']
      self.__long_term_memory = long_term_memory
    except TypeError:
      raise ValueError("Recieved dict is malformed")
    pass

  def get_summarized_identity(self):
    """
    A summary of the personas general identity
    INPUT
      None
    OUTPUT
      String summary of persona's basic identity
    EXAMPLE STR OUTPUT
      "Name: Dolores Heitmiller
       Age: 28
       Innate traits: hard-edged, independent, loyal
       Learned traits: Dolores is a painter who wants live quietly and paint 
         while enjoying her everyday life.
       Lifestyle: Dolores goes to bed around 11pm, sleeps for 7 hours, eats 
         dinner around 6pm.
    """
    return f"""Name: {self.__first_name + self.__last_name}
    Age: {self.__age}
    Innate Traits: {self.__innate_traits}
    Learnt Traits: {self.__long_term_memory.get_learned_traits()}
    Lifestyle: {self.__lifestyle}
    """

  def increment_age(self):
    self.__age += 1

  # Getters
  @property
  def full_name(self):
    return self.__first_name + self.__last_name

  @property
  def first_name(self):
    return self.__first_name

  @property
  def last_name(self):
    return self.__last_name

  @property
  def age(self):
    return self.__age
