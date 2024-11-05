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
from typing import Union

from reverie.backend_server.persona.core.Personality import Personality
from reverie.backend_server.persona.core.ShortTermMemory import ShortTermMemory
from reverie.backend_server.persona.core.SpatialMemory import SpatialMemory
from reverie.backend_server.persona.core.environment.Eyes import Eyes
from reverie.backend_server.persona.core.environment.interactors.DefaultInteractor import DefaultInteractor
from reverie.backend_server.persona.core.environment.interactors.Interactor import Interactor
from reverie.backend_server.persona.core.planning.DailyPlanning import DailyPlanning
from reverie.backend_server.persona.core.social.EmotionRegulator import EmotionalRegulator
from reverie.backend_server.persona.models.model import Model
from reverie.backend_server.world.World import World
from reverie.backend_server.world.world_objects.WorldObject import WorldObject
class Agent: 
  def __init__(self,
               personality:Personality, 
               emotional_regulator:EmotionalRegulator,
               short_term_memory:ShortTermMemory,
               spatial_memory:SpatialMemory,
               daily_planner:DailyPlanning,
               eyes:Eyes,
               model:Model,
               time_func,
               simulate=True):
    self.__personality = personality
    self.__emotional_regulator = emotional_regulator
    self.__short_term_memory = short_term_memory
    self.__spatial_memory = spatial_memory
    self.__daily_planner = daily_planner
    self.__eyes = eyes
    self.__simulated = simulate
    self.__default_interactor = DefaultInteractor(self.__daily_planner,self.__personality,model,time_func)
    self.__availible_interactors:list[Interactor] = []
    self.__current_interactor:Union[Interactor,None] = None

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
    if self.__simulated:
      self.__daily_planner.simulate_day()
    else:
      self.__daily_planner.plan_for_today()

  def select_interactor(self,object:WorldObject):
    for interactor in self.__availible_interactors:
      if interactor.is_compatible(object):
        return interactor
    return None

  def _check_interactor(self,object:Union[Interactor,None]=None):
    # TODO potentially more handling here rip
    if object is None and self.__current_interactor is not None:
      self.__current_interactor.disengage()
      self.__current_interactor = None
    elif object is not None and self.__current_interactor is not None:
      if object != self.__current_interactor:
        self.__current_interactor.disengage()
        self.__current_interactor = None
    elif object is not None and self.__current_interactor is None:
      self.__current_interactor = object
  def tick(self):
      """
      This is the main cognitive function where our main sequence is called. 
      Each tick is 1 minute.
      """
      current_time = self.__short_term_memory.get_current_time()
      if current_time.minute + current_time.hour + current_time.second == 0:
        self._plan_day()
        print(self.__daily_planner.to_dict())
      current_action = self.__daily_planner.current_task

      if current_action is None:
        self._check_interactor(None)
        print(f'No action is currently selected.')
        return
      if self.__simulated:
        action,time = current_action
        # get current action
        # tick current action using object.
        if action.target is None:
          # here we must mock percieve
          self._check_interactor(None)
          print(f'logs some memory for: {action.description}')
          # what, how, and when do we generate memories here, should we even?
          # maybe a method that decides if we should regenerate or continue on from some point? else we can just chill.
          # for this we need to associate task with the completed tasks and keep in mind when it should be completed.
        else:
          specific_interactor = self.select_interactor(action.target)
          interactor = self.__default_interactor if specific_interactor is None else specific_interactor
          self._check_interactor(interactor)
          print(f'{interactor.interact_with(action.target)}')
      else:
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

  def open_convo_session(self, convo_mode): 
    raise NotImplementedError()

  @property
  def name(self)->str:
    return self.__personality.full_name

  @property
  def status(self)->str:
    raise NotImplementedError()

  def _test_time(self):
    current_time = self.__short_term_memory.get_current_time()
    return current_time

  def state(self):
    return {
        "daily_planner" : self.__daily_planner.state(),
        "eyes" : self.__eyes.state(),
        "personality" : self.__personality.state(),
        "short_term_memory" : self.__short_term_memory.state(),
        "spatial_memory" : self.__spatial_memory.state()
      }
