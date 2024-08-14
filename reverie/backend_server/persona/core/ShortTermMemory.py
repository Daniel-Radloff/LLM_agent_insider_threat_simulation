class ShortTermMemory:
  def __init__(self,short_term:dict[str,str]) -> None:
    try:
      self.__currently = short_term['currently']
      self.__attention_span = int(short_term['attention_span'])
    except KeyError as e:
      raise ValueError(f"Dictionary does not contain expected keys:\n {e}")
    except TypeError as e:
      raise ValueError(f"Dictionary does not contain correct type:\n {e}")

  @property
  def attention_span(self):
    return self.__attention_span
  @property
  def currently(self):
    return self.__currently
