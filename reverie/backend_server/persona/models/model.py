from abc import ABC, abstractmethod
import re
from typing import Callable, Union
import sys

# this is so that paths are relative to reverie/backend_server/persona
# to provide drop in compatibility with existing path conventions
sys.path.append('../../')


class Model(ABC):
  # Todo, think of something good
  _default_system_prompt = ""
  _prompt_input_pattern = re.compile(r'!<INPUT \d+>')

  def __fill_in_prompt(self,prompt:str, prompt_parameters:list)->str:
    '''
    Loads a prompt from a relative file location and fills in parameters from provided list.
    Throws ValueError if list does not fill in all the inputs in the prompt.
    '''
    # For all the files, there is an optional comment section describing what the inputs do
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
  def __format_final_prompt(self,user_prompt:str,system_prompt:str)->dict[str,str]:
    pass

  @abstractmethod
  def __call_model(self,prompt_arguments:dict)->str:
    pass

  def run_inference(self,
                    user_prompt_location:str,
                    user_prompt_parameters:list,
                    system_prompt_parameters:list,
                    example_output:str,
                    validate:Callable[[str,str],str],
                    fail_safe_response:str,
                    special_instruction:Union[str,None]=None,
                    repeat=3,
                    system_prompt:Union[str,None]=None)->str:
    '''
    Provided the relative path of the prompt, the model will run inference on the prompt
    System prompt can be specified, else the default system prompt of the class will be used.
    The default system prompt requires one argument and thus a list of length 1
    giving a brief overview of the persona.
    Throws FileNotFoundError on file not found.
    Throws ValueError on parameter missmatches.
    '''
    # Memory alloc is expensive in python so im reusing the parameters :(
    # maybe if i use JIT compiler then i come back and change this
    match system_prompt:
      case str(system_prompt):
        pass
      case None:
        system_prompt = self._default_system_prompt
        if not len(system_prompt_parameters) == 1:
          raise ValueError("Using the default system prompt requires a prompt_parameter list of length 1, see doc string")

    with open(user_prompt_location,"r") as user_prompt_file:
      user_prompt = f"{self.__fill_in_prompt(user_prompt_file.read(),user_prompt_parameters)}\n"
    user_prompt += f"{special_instruction}\n" if special_instruction else ""
    user_prompt += f"An example response is:\n{example_output}"

    system_prompt = self.__fill_in_prompt(system_prompt, system_prompt_parameters)

    final_prompt = self.__format_final_prompt(user_prompt, system_prompt)

    for _ in range(repeat):
      try:
        response = self.__call_model(final_prompt)
        return validate(response,user_prompt)
      except ValueError:
        pass
      except:
        # TODO, impliment something more concrete here
        pass
    return fail_safe_response
