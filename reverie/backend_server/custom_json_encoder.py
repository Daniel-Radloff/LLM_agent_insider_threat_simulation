import json
import datetime
import re
from typing import Any

class CustomJSONEncoder(json.JSONEncoder):
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
    return super().default(o)
