import requests

from reverie.backend_server.persona.models.model import Model


class LLama3Instruct(Model):
  def __init__(self,model='llama3.1:8b-instruct-q8_0',seed=None) -> None:
    '''
    The model parameter is the model string that you want to target
    '''
    super().__init__()
    self._address = 'http://localhost:11434/api/generate'
    self._model_name = model

    # send empty prompt to load model into memory
    requests.post(self._address, json={'model' : self._model_name})

  def _format_final_prompt(self,user_prompt:str,system_prompt:str)->dict:
    return {
        'model' : self._model_name,
        'stream' : False,
        'prompt' : user_prompt,
        'system' : system_prompt
        }

  def _call_model(self,prompt_arguments:dict)->str:
    response = requests.post(self._address, json=prompt_arguments).json()
    print(response['response'])
    return response['response']

