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

  def tick(self):
      """
      This is the main cognitive function where our main sequence is called. 
      """
      events_around_us = self.__eyes.observe_environment()
      # some importance threshhold is needed to decide the following conditions
      #   being spoken to is not something we worry about because 
      #   that gets handled by the ear and mouth systems.

      # IF we see something we need to respond to:
        # we decide if we continue what we currently doing or respond
        # set action
      # else:
        # If doing something:
          # Determine next action to take
        # Else:
          # Determine next task and action to take

      # Perform selected action, be that an interaction of some kind or movement around the map.
      raise NotImplementedError()


  def simulated_world(self):
    '''
    This is a replacement for movement around the world. Instead, all the actions
    take place via communication with the LLM.
    '''

  def open_convo_session(self, convo_mode): 
    open_convo_session(self, convo_mode)

  @property
  def name(self)->str:
    return self.__personality.full_name

  @property
  def status(self)->str:
    raise NotImplementedError()
