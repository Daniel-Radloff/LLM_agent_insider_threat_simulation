def validate_number(response:str, _="")->str:
  '''
  Used a lot in core/social/EmotionRegulator.py as the validate function 
  '''
  try: 
    to_return = response.strip()
    # attempt to coerce value
    _ = int(to_return)
    return to_return
  except:
    raise ValueError("Response does not contain only an Integer")

def validate_hour_minute_time(response:str, _="")->str:
  '''
  Used a lot in core/planning/ as the validate function
  Check if the input string is a valid time in the format HH:MM.

  Args:
  - time_str (str): The time string to validate.

  Returns:
  - bool: True if the time is valid, False otherwise.
  '''
  split_time = list(map(int, response.split(':')))
  if len(split_time) != 2:
    raise ValueError("String is malformed")
  hours, minutes = split_time
  if 0 <= hours <= 23 and 0 <= minutes <= 59:
    return response
  else:
    raise ValueError
