"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: persona.py
Description: Defines the Persona class that powers the agents in Reverie. 

Note (May 1, 2023) -- this is effectively GenerativeAgent class. Persona was
the term we used internally back in 2022, taking from our Social Simulacra 
paper.
"""
import math
import sys
import datetime
import random

from reverie.backend_server.persona.core.Personality import Personality
from reverie.backend_server.persona.core.ShortTermMemory import ShortTermMemory
from reverie.backend_server.persona.core.SpatialMemory import SpatialMemory
from reverie.backend_server.persona.core.environment.Eyes import Eyes
from reverie.backend_server.persona.core.planning.DailyPlanning import DailyPlanning
from reverie.backend_server.persona.core.social.EmotionRegulator import EmotionalRegulator
from reverie.backend_server.world.World import World

from persona.memory_structures.spatial_memory import *
from persona.memory_structures.associative_memory import *
from persona.memory_structures.scratch import *

from persona.cognitive_modules.retrieve import *
from persona.cognitive_modules.reflect import *
from persona.cognitive_modules.execute import *
from persona.cognitive_modules.converse import *
from persona.cognitive_modules.plan import *

class Agent: 
  def __init__(self,
               personality:Personality, 
               emotional_regulator:EmotionalRegulator,
               short_term_memory:ShortTermMemory,
               spatial_memory:SpatialMemory,
               daily_planner:DailyPlanning,
               eyes:Eyes):
    self.__personality = personality
    self.__emotional_regulator = emotional_regulator
    self.__short_term_memory = short_term_memory
    self.__spatial_memory = spatial_memory
    self.__daily_planner = daily_planner
    self.__eyes = eyes

  def save(self, save_folder): 
    """
    Save persona's current state (i.e., memory). 

    INPUT: 
      save_folder: The folder where we wil be saving our persona's state. 
    OUTPUT: 
      None
    """
    raise NotImplementedError()

  def _plan_day(self):
    self.__daily_planner.plan_for_today()

  def take_action(self):
      """
      This is the main cognitive function where our main sequence is called. 

      INPUT: 
        maze: The Maze class of the current world. 
        personas: A dictionary that contains all persona names as keys, and the 
                  Persona instance as values. 
        curr_tile: A tuple that designates the persona's current tile location 
                   in (row, col) form. e.g., (58, 39)
        curr_time: datetime instance that indicates the game's current time. 
      OUTPUT: 
        execution: A triple set that contains the following components: 
          <next_tile> is a x,y coordinate. e.g., (58, 9)
          <pronunciatio> is an emoji.
          <description> is a string description of the movement. e.g., 
          writing her next novel (editing her novel) 
          @ double studio:double studio:common room:sofa
      """
      # Main cognitive sequence begins here. 
      self.__eyes.observe_environment()
      # retrieve relevent thoughts related to what we just saw.

      # Process these thoughts based on what we are currently doing,
      #   whats happening around us, and what we are trying to do.
      next_task = self.__daily_planner.next_task
      if next_task == None:
        # not doing anything? Find something to do.
        raise NotImplementedError()
      if next_task.target == None:
        # no target? find a memory that can give the location of something.
        raise NotImplementedError()
      possible_location = self.__spatial_memory.get_object_location(next_task.target)
      if self.__spatial_memory.current_location != possible_location:
        # Move to the location?
      # For the action we have determined to take, do we need to reflect on it before we act?

      # Perform selected action, be that an interaction of some kind or movement around the map.
      raise NotImplementedError()

  def open_convo_session(self, convo_mode): 
    open_convo_session(self, convo_mode)

  @property
  def name(self)->str:
    return self.__personality.full_name

  @property
  def status(self)->str:
    raise NotImplementedError()
