import json
import datetime
import re
from typing import Any

class CustomJSONEncoder(json.JSONEncoder):
  '''
  If something is not serializing as you would expect it to or you see a value
  is missing where you expected one in the output, enable the debug print on
  the dict instance of the default method.
  '''
  # vars is used to pass objects to the encoder
  # the output of vars when it encouters private attributes is 
  # a bit "mangled", this regex and case in the encoder "demangles"
  # the class attribute, improving readability.
  _class_private_attribute_regex = re.compile(r'^_[A-Z]([A-Z]|[a-z])+__([a-z]|_)*[a-z]$')

  def default(self, o: Any) -> Any:
    if isinstance(o, datetime.datetime):
      return o.strftime("%B %d, %Y, %H:%M:%S")
    if isinstance(o,str) and self._class_private_attribute_regex.match(o):
      return o.split("__")[1]
    # this skips anything that isn't json serializable
    if isinstance(o, dict):
      filtered_dict = {}
      for key, value in o.items():
        try:
          json.dumps(value, cls=CustomJSONEncoder)
          filtered_dict[key] = value
        except TypeError:
          #print(f"Warn: skipping pair: [{key},{value}]")
          pass
        o = filtered_dict
    return super().default(o)
