class ShortTermMemory:
  def __init__(self,short_term:dict[str,str]) -> None:
    try:
      self.currently = short_term['currently']
    except:
      raise ValueError("Dictionary does not contain expected value")
