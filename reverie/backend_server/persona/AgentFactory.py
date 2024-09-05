import json
from reverie.backend_server.world.World import World


class AgentBuilder:
  def __init__(self, world:World) -> None:
    pass

  def initialize_agent(self,target:str)->Agent:
    raise NotImplementedError()

  def __create_personality(self,target:str):
    identity_dict = json.load(open(target,'r'))
    return Personality(identity_dict)

  def __create_emotional_regulator(self,target:str):
    raise NotImplementedError()

  def __create_memory(self,target:str):
    raise NotImplementedError()

  def __create_spatial_memory(self,target:str):
    raise NotImplementedError()

  def __create_daily_planner(self,target:str):
    raise NotImplementedError()

  def __create_eyes(self,target:str):
    raise NotImplementedError()

  def __create_legs(self,target:str):
    raise NotImplementedError()

  def __create_cognition(self,target:str):
    raise NotImplementedError()

  def __build_agent(self,target:str):
    raise NotImplementedError()
