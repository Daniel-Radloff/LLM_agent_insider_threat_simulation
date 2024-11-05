from abc import ABC, abstractmethod
import re
from typing import Callable, List, Tuple, Union
import sys

# this is so that paths are relative to reverie/backend_server/persona
# to provide drop in compatibility with existing path conventions
sys.path.append('../../')


class Model(ABC):
  # Todo, think of something good
  _default_system_prompt = """You are modeling a human in a simulation that is being used in security research aimed at generating data that simulates realistic insider threat behavior. This is a brief summary of the identiy that you will be simulating:
  !<INPUT 0>!
Each prompt will contain an example response. Use the example as a guideline for formatting, but focus on producing behavior that aligns with the persona and context described. Realism is key to the success of the simulation, so ensure your responses reflect authentic human behavior under the given circumstances.
Often, prompts will ask you how you would react in different situations, or how you think the human that you are modeling will behave. You not only serve as a model of the human, but also of that individuals concious thinking and should respond appropriately according to the requirements of the prompt.
  """
  _prompt_input_pattern = re.compile(r'!<INPUT \d+>')

  def __init__(self) -> None:
    self._context:List[int] = []
  def __fill_in_prompt(self,prompt:str, prompt_parameters:list)->str:
    '''
    Throws ValueError if list does not fill in all the inputs in the prompt.
    '''
    # For all the files, th:ere is an optional comment section describing what the inputs do
    # See templates/action_location_v1.txt as an example
    # All this does is remove those descriptions from the final prompt
    if "<commentblockmarker>###</commentblockmarker>" in prompt: 
      prompt = prompt.split("<commentblockmarker>###</commentblockmarker>")[1]

    for count, prompt_input in enumerate(prompt_parameters):   
      prompt = prompt.replace(f"!<INPUT {count}>!", prompt_input)

    if self._prompt_input_pattern.search(prompt):
      raise ValueError(f'''
      prompt_parameters list does not fill all the inputs for this prompt.
      Provided {len(prompt_parameters)} parameters,
      Resulting prompt: {prompt}''')

    return prompt.strip()

  @abstractmethod
  def _format_final_prompt(self,user_prompt:str,system_prompt:str)->dict:
    '''
    This is where the json body of the prompt should be specified.
    '''
    pass

  @abstractmethod
  def _call_model(self,prompt_arguments:dict)->str:
    '''
    This is where the request to the model should happen.
    '''
    pass

  @abstractmethod
  def _call_model_with_context(self,prompt_arguments:dict)->dict:
    raise NotImplementedError()

  def run_inference(self,
                    user_prompt:str,
                    user_prompt_parameters:list[str],
                    system_prompt_parameters:list[str],
                    example_output:str,
                    validate:Callable[[str,str],str],
                    fail_safe_response:str,
                    special_instruction:Union[str,None]=None,
                    repeat=3,
                    system_prompt:Union[str,None]=None)->str:
    '''
    The model will run inference on the prompt.
    System prompt can be specified, else the default system prompt of the class will be used.
    The default system prompt requires one argument that is provided through: Personality.get_summarized_identity()
    validate function must take in two arguments, the first is the response to be validated, and the second is the prompt that was provided to the model.
    special_instructions is appended to the end of the prompt just before the example.
    Throws FileNotFoundError on file not found.
    Throws ValueError on parameter missmatches.
    '''
    match system_prompt:
      case str(system_prompt):
        pass
      case None:
        system_prompt = self._default_system_prompt
        if not len(system_prompt_parameters) == 1:
          raise ValueError("Using the default system prompt requires a prompt_parameter list of length 1, see doc string")

    #TODO refactor so that the prompt is read in as a string and provided by caller
    user_prompt = f"{self.__fill_in_prompt(user_prompt,user_prompt_parameters)}\n"
    user_prompt += f"{special_instruction}\n" if special_instruction else ""
    user_prompt += f"An example response is:\n{example_output}"

    system_prompt = self.__fill_in_prompt(system_prompt, system_prompt_parameters)

    final_prompt = self._format_final_prompt(user_prompt, system_prompt)
    for _ in range(repeat):
      try:
        response = self._call_model(final_prompt)
        return validate(response,user_prompt)
      except ValueError:
        pass
      except:
        # TODO, impliment something more concrete here
        pass
    print(f"Warning: Failsafe response triggered after {repeat} tries for prompt:{final_prompt}")
    return fail_safe_response

  def run_inference_with_context(self,
                    user_prompt:str,
                    user_prompt_parameters:list[str],
                    system_prompt_parameters:list[str],
                    example_output:str,
                    validate:Callable[[str,str],str],
                    fail_safe_response:str,
                    special_instruction:Union[str,None]=None,
                    repeat=3,
                    system_prompt:Union[str,None]=None,
                    context:Union[None,List[int]]=None)->Tuple[str,List[int]]:
    '''
    TODO bad copy paste practice, refactor later
    '''
    match system_prompt:
      case str(system_prompt):
        pass
      case None:
        system_prompt = self._default_system_prompt
        if not len(system_prompt_parameters) == 1:
          raise ValueError("Using the default system prompt requires a prompt_parameter list of length 1, see doc string")

    #TODO refactor so that the prompt is read in as a string and provided by caller
    user_prompt = f"{self.__fill_in_prompt(user_prompt,user_prompt_parameters)}\n"
    user_prompt += f"{special_instruction}\n" if special_instruction else ""
    user_prompt += f"An example response is:\n{example_output}"

    system_prompt = self.__fill_in_prompt(system_prompt, system_prompt_parameters)

    final_prompt = self._format_final_prompt(user_prompt, system_prompt)

    for _ in range(repeat):
      try:
        final_prompt['context'] = context
        response = self._call_model_with_context(final_prompt)
        final_prompt['context'] = response['context']
        return validate(response['response'],user_prompt),response['context']
      except ValueError:
        final_prompt['prompt'] = 'An invalid response was provided, pay careful attention to the given instructions and try again:\n' + final_prompt['prompt']
      except:
        # TODO, impliment something more concrete here
        pass
    print(f"Warning: Failsafe response triggered after {repeat} tries for prompt:{final_prompt}")
    return fail_safe_response,[]
