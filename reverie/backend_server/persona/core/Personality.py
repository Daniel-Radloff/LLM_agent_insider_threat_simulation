class Personality:
  def __init__(self,
               personality:dict[str,str]) -> None:
    try:
      self.__first_name:str = personality['first_name']
      self.__last_name:str = personality['last_name']
      self.__age:str = personality['age']
      self.__innate_traits:str = personality['innate_traits']
      self.__lifestyle:str = personality['lifestyle']
      self.__learned_traits:str = personality['learned_traits']
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
    Learnt Traits: {self.__learned_traits}
    Lifestyle: {self.__lifestyle}
    """

  def _revise_learned_traits(self,new_traits:str):
    '''
    Sets new learned traits. Defined as protected and meant to be used in
    LongTermMemory.
    '''
    self.__learned_traits = new_traits
  def increment_age(self):
    self.__age += 1

  # Getters
  @property
  def full_name(self):
    return self.__first_name + " " + self.__last_name

  @property
  def first_name(self):
    return self.__first_name

  @property
  def last_name(self):
    return self.__last_name

  @property
  def age(self):
    return self.__age

  @property
  def lifestyle(self):
    return self.__lifestyle
