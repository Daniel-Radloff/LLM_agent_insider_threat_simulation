from reverie.backend_server.persona.core.Personality import Personality
from reverie.backend_server.persona.core.helpers import validate_number
from reverie.backend_server.persona.models.model import Model


class EmotionalRegulator:
  def __init__(self,personality:Personality,llm:Model) -> None:
    self.__personality = personality
    self.__model = llm

  def determine_emotional_impact(self, event_type:str, description:str)->int:
    prompt_input = [self.__personality.full_name,
                    description]
    system_input = [self.__personality.get_summarized_identity()]
    example_output = "5"
    special_instruction = "The output should ONLY contain ONE integer value on the scale of 1 to 10."
    fail_safe = "4"
    if "is idle" in description: 
      return 1
    match event_type:
      case "event":
        output =  self.__model.run_inference("templates/impact_event.txt",
                                             prompt_input,
                                             system_input,
                                             example_output,
                                             validate_number,
                                             fail_safe,
                                             special_instruction=special_instruction)
        return int(output)
      case"chat": 
        output =  self.__model.run_inference("templates/impact_chat.txt",
                                             prompt_input,
                                             system_input,
                                             example_output,
                                             validate_number,
                                             fail_safe,
                                             special_instruction=special_instruction)
        return int(output)
      case"thought": 
        output =  self.__model.run_inference("templates/impact_thought.txt",
                                             prompt_input,
                                             system_input,
                                             example_output,
                                             validate_number,
                                             fail_safe,
                                             special_instruction=special_instruction)
        return int(output)
    return 1
