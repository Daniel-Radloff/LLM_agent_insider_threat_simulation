from dataclasses import dataclass
from datetime import datetime
from typing import Callable


@dataclass
class Action:
  '''
  Some action that needs to take place at some point
  '''
  def __init__(self, name, duration, prerequisites=None, deadline=None):
    self.name = name
    self.duration = duration
    self.prerequisites = prerequisites or []
    self.deadline = deadline

  def __str__(self):
    return f'{self.name}'

class LongtermPlanning:
  '''
  Acts as a checklist for the agent to act out
  a given scenario role and their different actions.

  pop last element of actions_to_complete and append it to completed_actions when moving
  '''
  def __init__(self,
               actions_to_complete,
               completed_actions,
               world_time:Callable[[],datetime]
               ) -> None:
    self.actions_to_complete = actions_to_complete
    self.completed_actions = completed_actions
    self.world_time = world_time

  def complete_action(self,action):
    '''
    Marks an action as completed, progressing
    the simulation of the scenario to the next
    stage.
    '''
    if action in self.actions_to_complete:
      self.actions_to_complete.remove(action)

  def get_context(self):
    '''
    Get the context of the current day with regards to the
    scenario that is being simulated.
    '''
    next_action = self.actions_to_complete[-1]
    last_action = self.completed_actions[-1]
    last = f'The last key action that has been completed in the scenario was: "{last_action}".'
    next = f'The next action that needs completion in this scenario is "{next_action}", and must be completed on {next_action.deadline}.' 
    return '\n'.join([last,next]) + '\n'

