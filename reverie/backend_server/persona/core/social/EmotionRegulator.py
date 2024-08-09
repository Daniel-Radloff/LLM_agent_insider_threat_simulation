class EmotionalRegulator:
  def run_gpt_prompt_event_poignancy(persona, event_description, test_input=None, verbose=False)->int: 
    prompt_template = "persona/prompt_template/templates/poignancy_event_v1.txt"
    prompt_input = [persona.scratch.name,
                    persona.scratch.get_str_iss(),
                    persona.scratch.name,
                    event_description]

    prompt = generate_prompt(prompt_input, prompt_template)
    example_output = "5"
    special_instruction = "The output should ONLY contain ONE integer value on the scale of 1 to 10."
    fail_safe = "4"
    output = safe_generate_response(prompt, example_output, validate_number, fail_safe, special_instruction)
    return int(output)

  def run_gpt_prompt_thought_poignancy(persona, event_description, test_input=None, verbose=False): 
    def create_prompt_input(persona, event_description, test_input=None): 
      prompt_input = [persona.scratch.name,
                      persona.scratch.get_str_iss(),
                      persona.scratch.name,
                      event_description]
      return prompt_input
    
    def __func_clean_up(gpt_response, prompt=""):
      gpt_response = int(gpt_response.strip())
      return gpt_response

    def __func_validate(gpt_response, prompt=""): 
      try: 
        __func_clean_up(gpt_response, prompt)
        return True
      except:
        return False 

    def get_fail_safe(): 
      return 4

    def __chat_func_clean_up(gpt_response, prompt=""):
      gpt_response = int(gpt_response)
      return gpt_response

    def __chat_func_validate(gpt_response, prompt=""):
      try: 
        __func_clean_up(gpt_response, prompt)
        return True
      except:
        return False 

    print ("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 8")
    gpt_param = {"engine": "text-davinci-002", "max_tokens": 15, 
                 "temperature": 0, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "persona/prompt_template/v3_ChatGPT/poignancy_thought_v1.txt"
    prompt_input = create_prompt_input(persona, event_description)
    prompt = generate_prompt(prompt_input, prompt_template)
    example_output = "5"
    special_instruction = "The output should ONLY contain ONE integer value on the scale of 1 to 10."
    fail_safe = get_fail_safe()
    output = ChatGPT_safe_generate_response(prompt, example_output, special_instruction, 3, fail_safe,
                                            __chat_func_validate, __chat_func_clean_up, True)
    if output != False: 
      return output, [output, prompt, gpt_param, prompt_input, fail_safe]

  def run_gpt_prompt_chat_poignancy(persona, event_description, test_input=None, verbose=False)->int:
    prompt_input = [persona.scratch.name,
                    persona.scratch.get_str_iss(),
                    persona.scratch.name,
                    event_description]
    prompt_template = "persona/prompt_template/template/poignancy_chat_v1.txt"
    prompt = generate_prompt(prompt_input, prompt_template)

    example_output = "5"
    special_instruction = "The output should ONLY contain ONE integer value on the scale of 1 to 10."
    fail_safe = "4"
    output = safe_generate_response(prompt, example_output, validate_number, fail_safe, special_instruction)
    return int(output)
