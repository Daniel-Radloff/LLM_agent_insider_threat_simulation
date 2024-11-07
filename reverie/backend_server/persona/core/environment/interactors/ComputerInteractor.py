from datetime import datetime
from typing import Callable, Union
from collections import deque
from reverie.backend_server.persona.core.Personality import Personality
from reverie.backend_server.persona.core.environment.interactors.Interactor import Interactor
from reverie.backend_server.persona.core.planning.DailyPlanning import DailyPlanning
from reverie.backend_server.persona.models.model import Model
from reverie.backend_server.world.world_objects.WorldObject import WorldObject


class ComputerInteractor(Interactor):
  def __init__(self, daily_planner: DailyPlanning,personality:Personality,model:Model,time_func:Callable[[],datetime]) -> None:
    super().__init__(['73621'], daily_planner,personality,model,time_func)
    self.current_progress = "just started"
    self.last_command = None 

  def interact_with(self, target: WorldObject):
    '''
    Construct a prompt to perform an action
    This will call the LLM multiple times, all taking place kinda within the minute if that makes sense.
    '''
    current_task = self._daily_planner.current_task
    if current_task is None:
      raise RuntimeError('interact_with, must never be called when there is no task being done.')
    task,time = current_task

    def val(r:str,_:str)->str:
      print(f'BOT RESPONSE:\n{r}')
      return r.split('---\n')[1]
    
    while target.ready_for_interaction:
      # Interaction with the object
      screen = target.interact()
      print(f"SYSTEM RESPONSE:\n{screen}")
      self.current_progress = self.form_context(
          self.current_progress,
          task.description,
          self.last_command,
          screen)
      availible_actions = target.availible_actions
      system_prompt = f"""You are modeling a human in a simulation that is being used in security research aimed at generating data that simulates realistic insider threat behavior. This is a brief summary of the identiy that you will be simulating:
    !<INPUT 0>!
  You are currently interacting with a sytem to perform the following task: {task} Taking place {time.hour_min_str}. The system is simulated and is very basic in its capibility, so things like "cd ../ && ls" or the ";" linux operators will not work, and most commands wont support flags. Each line must be executed one at a time. The systems name is '{target.name}'. The system has the following commands availible to you:\n{availible_actions}\n\n
  take note of which commands are related to which applications (email vs file manager) 
    """
      prompt = f"The time is currently {target.object_time}. Here is some contextual infromation that you have thought about for yourself:\n{self.current_progress}\nOn the screen is the following after you executed your last command:\n{screen}. When responding, think about what you want to do, before typing:\n---\n<the command you want to use>\n"
      response = self._model.run_inference(
          prompt,
          [],
          [self._personality.get_summarized_identity()],
          "The system screen is currently off, I want to check my emails so I need to turn the system on before i can do anything else. I will use the poweron command\n---\npoweron\n\n",
          val,
          target.availible_actions,
          system_prompt=system_prompt
        )
      target.interact(response)
      self.last_command = response
    return self.current_progress

  def form_context(self,
                   previous_context:str,
                   current_task:str,
                   last_command:Union[None,str],
                   command_output:Union[None,str]
                   )->str:

    """
    Generate a new context hint based on the previous context, 
    the last action taken, and the current task or goal.
    """
    context_hint = previous_context
    if last_command:
        command = f"\nThe last command executed was: {last_command}."
    else:
        command = "\nNo command has been executed yet."

    # Add the current task or goal to guide the next action
    prompt = f"You are currently in the process of completing the task: '{current_task}'.\n The last progress report/contextual hint that you have made for yourself was this:\n{context_hint}\nThe last command you executed on the system was:'{command}' with the output being the following:\n{command_output} Your task is to now generate a new contextual hint/thought about the next command you want to use to progress further."
    return self._model.run_inference(
        prompt,
        [],
        [self._personality.get_summarized_identity()],
        "The system screen is currently off, I want to check my emails so I need to turn the system on before i can do anything else. I will use the poweron command\n---\npoweron\n\n",
        lambda r,_:r,
        command
      )

  def disengage(self):
    print('Default Interactor Disengaged')
    self._current_context = None
    # Potentially log out or not depending on LLM decision
