from reverie.backend_server.persona.core.ShortTermMemory import ShortTermMemory
from reverie.backend_server.persona.core.LongTermMemory import LongTermMemory
from reverie.backend_server.persona.core.SpatialMemory import SpatialMemory
from reverie.backend_server.persona.core.planning.DailyPlanning import DailyPlanning


class Cognition:
  def __init__(self,
               short_term_memory:ShortTermMemory,
               daily_plan:DailyPlanning,
               spatial_memory:SpatialMemory
               ) -> None:
    self.__short_term_memory = short_term_memory
    self.__daily_plan = daily_plan
    self.__spatial_memory = spatial_memory
    pass

  def determine_what_to_do(self):
    pass

  # TODO: through experimentation, embeddings can be used here.
  #   once all memory is consolidated into one class, that may
  #   become one way of determining relevance.
  def _associate_object_with_task(self):
    '''
    Interacts with SpatialMemory and DailyPlanning.
    It finds an object that is the most likely candidate to
    be able to complete a given task.
    '''
    objects = self.__spatial_memory.get_known_objects()
    current_task = self.__daily_plan.current_task
    
