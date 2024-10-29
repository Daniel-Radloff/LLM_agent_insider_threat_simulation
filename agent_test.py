from reverie.backend_server.persona.Agent import Agent
from reverie.backend_server.persona.AgentFactory import AgentBuilder
from reverie.backend_server.world.World import World
from reverie.backend_server.world.WorldFactory import WorldFactory
import sys
import os


def tick_test(agent:Agent, world:World):
  '''
  Testing how the agent handles ticking 
  '''
  agent.tick()
  for _ in range(60*7):
    world._tick()

  agent.tick()

if __name__ == '__main__':
  # testing init methods, does not guarantee that all the stuff is working obviously
  world_factory = WorldFactory()
  world = world_factory.produce_world('./assets/world/testing')
  agent_factory = AgentBuilder(world)
  agent = agent_factory.initialize_agent('./assets/personalities/test')

  # testing world time with agent time syncronization
  print(agent._test_time())
  print(world.current_time)
  world._tick()
  print(agent._test_time())
  print(world.current_time)
  world._tick_back()

  tick_test(agent,world)
