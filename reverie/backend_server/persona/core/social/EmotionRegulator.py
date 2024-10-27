from reverie.backend_server.persona.core.Personality import Personality
from reverie.backend_server.persona.core.helpers import validate_number
from reverie.backend_server.persona.models.model import Model
import os


class EmotionalRegulator:
  def __init__(self,personality:Personality,llm:Model) -> None:
    self.__personality = personality
    self.__model = llm
    self._template_dir = os.path.join(os.path.dirname(__file__), 'templates')

  def determine_emotional_impact(self, event_type:str, description:str)->int:
    if event_type not in ["event","chat","thought"]:
      raise ValueError("event type must be an event,chat,or thought")
    with open(os.path.join(self._template_dir, f"impact_{event_type}.txt"),"r") as file:
      prompt = file.read()
    prompt_input = [self.__personality.full_name,
                    description]
    system_input = [self.__personality.get_summarized_identity()]
    example_output = "5"
    special_instruction = "The output should ONLY contain ONE integer value on the scale of 1 to 10."
    fail_safe = "4"
    if "is idle" in description: 
      return 1
    output =  self.__model.run_inference(prompt,
                                         prompt_input,
                                         system_input,
                                         example_output,
                                         validate_number,
                                         fail_safe,
                                         special_instruction=special_instruction)
    return int(output)
