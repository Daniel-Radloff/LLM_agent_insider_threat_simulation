def validate_number(response:str, _="")->str:
  '''
  Used a lot as the validate function in the poignancy functions
  '''
  try: 
    to_return = response.strip()
    # attempt to coerce value
    _ = int(to_return)
    return to_return
  except:
    raise ValueError("Response does not contain only an Integer")
