from collections.abc import Callable
from datetime import datetime
import json
from reverie.backend_server.persona.Agent import Agent
from reverie.backend_server.persona.core.Cognition import Cognition
from reverie.backend_server.persona.core.Personality import Personality
from reverie.backend_server.persona.core.ShortTermMemory import ShortTermMemory
from reverie.backend_server.persona.core.SpatialMemory import SpatialMemory
from reverie.backend_server.persona.core.environment.Eyes import Eyes
from reverie.backend_server.persona.core.environment.Legs import Legs
from reverie.backend_server.persona.core.planning.DailyPlanning import DailyPlanning, DailyPlanningData, Task, TimePeriod
from reverie.backend_server.persona.core.social.EmotionRegulator import EmotionalRegulator
from reverie.backend_server.persona.models.Llama3Instruct import LLama3Instruct
from reverie.backend_server.persona.models.model import Model
from reverie.backend_server.world.World import World
from reverie.backend_server.world.world_objects.WorldObject import WorldObject


class AgentBuilder:
  def __init__(self, world:World) -> None:
    self.__world = world
    self.__llm = LLama3Instruct()

  def initialize_agent(self,target:str)->Agent:
    # TODO: test this
    time_func = lambda : self.__world.current_time
    personality = self.__create_personality(
        f'{target}/personality.json')
    emotional_regulator = EmotionalRegulator(personality,self.__llm)
    short_term_memory = self.__create_memory(
        f'{target}/short_term_memory.json',
        time_func,
        emotional_regulator,personality)
    spatial_memory = self.__create_spatial_memory(
        f'{target}/spatial_memory.json')
    daily_planner = self.__create_daily_planner(
        f'{target}/daily_planner.json',
        personality,
        short_term_memory,
        spatial_memory,
        self.__world._objects())
    eyes = self.__create_eyes(
        f'{target}/eyes.json',
        spatial_memory,
        short_term_memory)
    cognition = Cognition(short_term_memory,daily_planner,spatial_memory)

    # Make agent

    agent = Agent(personality,emotional_regulator,short_term_memory,spatial_memory,daily_planner,eyes)

    # Attach other objects to agent
    legs = Legs(self.__world,spatial_memory,agent)

    # End
    return agent

  def __create_personality(self,target:str):
    identity_dict = json.load(open(target,'r'))
    return Personality(identity_dict)

  def __create_memory(self,
                      target:str,
                      time_func:Callable[[],datetime],
                      emotional_regulator:EmotionalRegulator,
                      personality:Personality,
                      )->ShortTermMemory:
    short_term_data = json.load(open(target,'r'))
    return ShortTermMemory(short_term_data,time_func,emotional_regulator,personality)

  def __create_spatial_memory(self,target:str):
    data = json.load(open(target,'r'))
    return SpatialMemory(data,self.__world)

  def __create_daily_planner(self,
                             target:str,
                             personality:Personality,
                             short_term_memory:ShortTermMemory,
                             spatial_memory:SpatialMemory,
                             world_objects:dict[str,WorldObject],
                             )->DailyPlanning:
    def create_daily_planning_data_object(data:dict):
      time_format = "%Y-%m-%d %H:%M:%S"
      wake_up_time = datetime.strptime(data['wake_up_time'],time_format)

      schedule = []
      for time_period_data,task_data in data['schedule']:
        start = datetime.strptime(time_period_data['start'],time_format)
        end = datetime.strptime(time_period_data['end'],time_format)
        time_period = TimePeriod(start,end)
        if 'target' in task_data:
          target = world_objects[task_data['target']]
        else:
          target = None
        task = Task(task_data['description'],target)
        schedule.append((time_period, target))

      incompleted_tasks = []
      for task_data in data['incompleted_tasks']:
        if 'target' in task_data:
          target = world_objects[task_data['target']]
        else:
          target = None
        task = Task(task_data['description'],target)
        incompleted_tasks.append(target)
      return DailyPlanningData(wake_up_time,schedule,incompleted_tasks)

    daily_planning_data = json.load(open(target,'r'))
    standard_tasks = daily_planning_data['standard_tasks']
    current_daily_plan = create_daily_planning_data_object(daily_planning_data['data'])
    previous_daily_plan = create_daily_planning_data_object(daily_planning_data['previous'])
    current_steps = daily_planning_data['steps']
    return DailyPlanning(self.__llm,personality,short_term_memory,spatial_memory,standard_tasks,current_daily_plan,previous_daily_plan,current_steps)

  def __create_eyes(self,
                    target:str,
                    spatial_memory:SpatialMemory,
                    short_term_memory:ShortTermMemory):
    eye_data = json.load(open(target,'r'))
    return Eyes(eye_data,self.__world,spatial_memory,short_term_memory)

  def __create_cognition(self,target:str):
    raise NotImplementedError()

  def __create_legs(self,target:str):
    raise NotImplementedError()

  def __build_agent(self,target:str):
    raise NotImplementedError()
