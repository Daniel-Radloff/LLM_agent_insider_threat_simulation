from reverie.backend_server.persona.core.ShortTermMemory import ShortTermMemory
from reverie.backend_server.persona.core.LongTermMemory import LongTermMemory
from reverie.backend_server.persona.core.planning.DailyPlanning import DailyPlanning


class Cognition:
  def __init__(self,
               parameters:dict,
               short_term_memory:ShortTermMemory,
               long_term_memory:LongTermMemory,
               daily_plan:DailyPlanning) -> None:
    self.__short_term_memory = short_term_memory
    self.__long_term_memory = long_term_memory
    self.__daily_plan = daily_plan
    pass

  def determine_what_to_do(self):
    pass


