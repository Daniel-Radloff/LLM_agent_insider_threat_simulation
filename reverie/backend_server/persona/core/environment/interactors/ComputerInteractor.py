from datetime import datetime
from typing import Callable
from reverie.backend_server.persona.core.Personality import Personality
from reverie.backend_server.persona.core.environment.interactors.Interactor import Interactor
from reverie.backend_server.persona.core.planning.DailyPlanning import DailyPlanning
from reverie.backend_server.persona.models.model import Model
from reverie.backend_server.world.world_objects.WorldObject import WorldObject


class ComputerInteractor(Interactor):
  def __init__(self, daily_planner: DailyPlanning,personality:Personality,model:Model,time_func:Callable[[],datetime]) -> None:
    super().__init__([], [], daily_planner,personality,model,time_func)

  def interact_with(self, target: WorldObject):
    '''
    Construct a prompt to perform an action
    '''
    if self._current_context == []:
      self._current_context = None
    def val(r:str,_:str)->str:
      return r
    current_task = self._daily_planner.current_task
    if current_task is None:
      raise RuntimeError('interact_with, must never be called when there is no task being done.')
    task,time = current_task
    if self._current_context is None:
      prompt = f"You are currently in the process of completing the following task:\n{task.description} {time.hour_min_str}\n\nThe current time is: {self._world_time}Respond with a verb/action you perform to interact with the object:{target.name} in the context of the task and timeframe. Keep in mind who you are."
    else:
      prompt = f"The time is now {self._world_time}, continue interacting (or not) with the object: {target.name}. Remember the end time for this task."
    response,context = self._model.run_inference_with_context(
        prompt,
        [],
        [self._personality.get_summarized_identity()],
        "make food, nothing, etc",
        val,
        "nothing",
        context=self._current_context
      )
    self._current_context = context
    return response

  def disengage(self):
    print('Default Interactor Disengaged')
    self._current_context = None
