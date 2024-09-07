from collections.abc import Callable
from datetime import datetime
import json
from reverie.backend_server.persona.core.Personality import Personality
from reverie.backend_server.persona.core.ShortTermMemory import ShortTermMemory
from reverie.backend_server.persona.core.social.EmotionRegulator import EmotionalRegulator
from reverie.backend_server.persona.models.Llama3Instruct import LLama3Instruct
from reverie.backend_server.persona.models.model import Model
from reverie.backend_server.world.World import World


class AgentBuilder:
  def __init__(self, world:World) -> None:
    self.__world = world
    self.__llm = LLama3Instruct()

  def initialize_agent(self,target:str)->Agent:
    # TODO: test this
    time_func = lambda : self.__world.current_time
    personality = self.__create_personality(f'{target}/personality.json')
    emotional_regulator = EmotionalRegulator(personality,self.__llm)
    short_term_memory = self.__create_memory
    raise NotImplementedError()

  def __create_personality(self,target:str):
    identity_dict = json.load(open(target,'r'))
    return Personality(identity_dict)

  def __create_memory(self,
                      target:str,
                      time_func:Callable[[],datetime],
                      emotional_regulator:EmotionalRegulator,
                      personality:Personality,
                      )->ShortTermMemory:
    short_term_data = json.load(open(f'{target}/short_term_memory.json','r'))
    return ShortTermMemory(short_term_data,time_func,emotional_regulator,personality)

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
