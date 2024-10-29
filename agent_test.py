from reverie.backend_server.persona.Agent import Agent
from reverie.backend_server.persona.AgentFactory import AgentBuilder
from reverie.backend_server.world.World import World
from reverie.backend_server.world.WorldFactory import WorldFactory
import sys
import os
import json
import argparse

def tick_test(agent: Agent, world: World):
  '''Testing how the agent handles ticking'''
  agent.tick()
  for _ in range(60 * 7):
    world._tick()
  agent.tick()

def save(name, agent):
  os.makedirs(name, exist_ok=True)
  state = agent.state()
  with open(f'{name}/daily_planner.json', 'w') as file:
    json.dump(state['daily_planner'], file, indent=2)
  with open(f'{name}/eyes.json', 'w') as file:
    json.dump(state['eyes'], file, indent=2)
  with open(f'{name}/personality.json', 'w') as file:
    json.dump(state['personality'], file, indent=2)
  with open(f'{name}/short_term_memory.json', 'w') as file:
    json.dump(state['short_term_memory'], file, indent=2)
  with open(f'{name}/spatial_memory.json', 'w') as file:
    json.dump(state['spatial_memory'], file, indent=2)

if __name__ == '__main__':
  # Setting up argument parsing
  parser = argparse.ArgumentParser(description='Run tests on the agent and world.')
  parser.add_argument('--test_type', nargs='+', type=str, required=True, 
                      help='Specify the type of test to run (e.g., tick, save).')
  parser.add_argument('--world_path', type=str, required=True, 
                      help='Path to the world assets.')
  parser.add_argument('--personality_path', type=str, required=True, 
                      help='Path to the personality assets.')
  args = parser.parse_args()

  # Initializing world and agent
  world_factory = WorldFactory()
  world = world_factory.produce_world(f'./assets/world/{args.world_path}')
  agent_factory = AgentBuilder(world)
  agent = agent_factory.initialize_agent(f'./assets/personalities/{args.personality_path}')

  # Testing world time with agent time synchronization
  print(agent._test_time())
  print(world.current_time)
  world._tick()
  print(agent._test_time())
  print(world.current_time)
  world._tick_back()

  # Running the specified test type
  for test_type in args.test_types:
    if test_type == 'tick':
      print("Running tick test...")
      tick_test(agent, world)
    elif test_type == 'save':
      print("Running save test...")
      save('output', agent)  # You can customize the output directory name if needed
    else:
      print(f"Unknown test type: {test_type}. Skipping.")

  print("All tests completed.")
