import json
import datetime
from typing import Any

class CustomJSONEncoder(json.JSONEncoder):
  def default(self, o: Any) -> Any:
    if isinstance(o, datetime.datetime):
      return o.strftime("%B %d, %Y, %H:%M:%S")
    return super().default(o)
