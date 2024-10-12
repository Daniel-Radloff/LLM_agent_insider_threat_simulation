from reverie.backend_server.world.World import World
from reverie.backend_server.persona.core.SpatialMemory import SpatialMemory
from reverie.backend_server.persona.core.ShortTermMemory import ShortTermMemory


class Eyes:
  def __init__(self,
               parameters:dict,
               environment:World,
               spatial_memory:SpatialMemory,
               short_term_memory:ShortTermMemory) -> None:
    try: 
      self.__vision_radius = int(parameters['vision_radius'])
      self.__environment = environment
      self.__spatial_memory = spatial_memory
      self.__short_term_memory = short_term_memory
    except:
      raise ValueError("Dictionary does not contain expected value")

  def observe_environment(self):
    surrounding_environment = self.__environment.get_surrounding_environment(
        (self.__spatial_memory.current_location.x, self.__spatial_memory.current_location.y),
        self.__vision_radius)

    observed_events = self.__spatial_memory.process_visual_input(surrounding_environment)

    # limit to attention bandwidth
    observed_events = observed_events[:self.__short_term_memory.attention_span]

    # create a set of the observed events in the area so that we can filter duplicates
    observed_event_set = set()
    for event in observed_events: 
      observed_event_set.add(event)
    # Process the events that are happening around us

      # We retrieve the latest persona.scratch.retention events. If there is  
      # something new that is happening (that is, p_event not in latest_events),
      # then we add that event to the a_mem and return it. 
      # Review Note:
      # Surely the same event cannot occur in two places, if this is the case, then why call this every time?
    return self.__short_term_memory.process_events(list(observed_event_set))

  @property
  def vision_radius(self):
    return self.__vision_radius
