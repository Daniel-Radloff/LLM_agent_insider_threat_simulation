"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: gpt_structure.py
Description: Wrapper functions for calling OpenAI APIs.
"""
import openai
import time 
from typing import Callable

from utils import *

openai.api_key = openai_api_key

def temp_sleep(seconds=0.1):
  time.sleep(seconds)

def run_inference(prompt): 
  """
  Given a prompt and a dictionary of GPT parameters, make a request to OpenAI
  server and returns the response. 
  ARGS:
    prompt: a str prompt
    gpt_parameter: a python dictionary with the keys indicating the names of  
                   the parameter and the values indicating the parameter 
                   values.   
  RETURNS: 
    a str of GPT-3's response. 
  """
  # temp_sleep()
  try: 
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo", 
    messages=[{"role": "user", "content": prompt}]
    )
    return completion["choices"][0]["message"]["content"]
  
  except: 
    print ("ChatGPT ERROR")
    return "ChatGPT ERROR"

def safe_generate_response(prompt:str, 
                                   example_output:str,
                                   validate:Callable[[str,str],str],
                                   fail_safe_response:str,
                                   special_instruction:str="",
                                   repeat=3)->str: 
  '''
    Attempts to generate a response several times, uses the first 
    response that passes the validate function.
    Validate must take in two arguments: 
    1) the current response of the model
    2) the original prompt the model was given
    It is up to the validate function to check any formatting
    validate must throw a ValueError
    Special instructions such as a format specification can be
    passed via special_instruction.
  '''

  modified_prompt = f"{prompt}\n"
  modified_prompt += f"{special_instruction}\n"
  modified_prompt += f"Example output:\n{example_output}"

  for _ in range(repeat): 
    try: 
      curr_gpt_response = run_inference(modified_prompt).strip()
      # Review Note:
      # func_validate should validate the output and return the value surely. 
      # Why make two functions
      return validate(curr_gpt_response, prompt)
    except ValueError:
      pass
    except:
      # TODO, impliment something more concrete here
      pass
  return fail_safe_response

def generate_prompt(curr_input:list[str], prompt_lib_file): 
  """
  Takes in the current input (e.g. comment that you want to classifiy) and 
  the path to a prompt file. The prompt file contains the raw str prompt that
  will be used, which contains the following substr: !<INPUT>! -- this 
  function replaces this substr with the actual curr_input to produce the 
  final promopt that will be sent to the GPT3 server. 
  ARGS:
    curr_input: the list of string inputs for the prompt.
    prompt_lib_file: the path to the promopt file. 
  RETURNS: 
    a str prompt that will be sent to OpenAI's GPT server.  
  """
  with open(prompt_lib_file, "r") as prompt_file:
    prompt = prompt_file.read()

  # For all the files, there is an optional comment section describing what the inputs do
  # See v3_ChatGPT/action_location_v1.txt as an example
  # All this does is remove those descriptions from the final prompt
  if "<commentblockmarker>###</commentblockmarker>" in prompt: 
    prompt = prompt.split("<commentblockmarker>###</commentblockmarker>")[1]

  for count, prompt_input in enumerate(curr_input):   
    prompt = prompt.replace(f"!<INPUT {count}>!", prompt_input)
  return prompt.strip()

def get_embedding(text, model="text-embedding-ada-002"):
  text = text.replace("\n", " ")
  if not text: 
    text = "this is blank"
  return openai.Embedding.create(
          input=[text], model=model)['data'][0]['embedding']

if __name__ == '__main__':
  gpt_parameter = {"engine": "text-davinci-003", "max_tokens": 50, 
                   "temperature": 0, "top_p": 1, "stream": False,
                   "frequency_penalty": 0, "presence_penalty": 0, 
                   "stop": ['"']}
  curr_input = ["driving to a friend's house"]
  prompt_lib_file = "prompt_template/test_prompt_July5.txt"
  prompt = generate_prompt(curr_input, prompt_lib_file)

  def __func_validate(gpt_response): 
    if len(gpt_response.strip()) <= 1:
      return False
    if len(gpt_response.strip().split(" ")) > 1: 
      return False
    return True
  def __func_clean_up(gpt_response):
    cleaned_response = gpt_response.strip()
    return cleaned_response

  output = safe_generate_response(prompt, 
                                 gpt_parameter,
                                 5,
                                 "rest",
                                 __func_validate,
                                 __func_clean_up,
                                 True)

  print (output)
