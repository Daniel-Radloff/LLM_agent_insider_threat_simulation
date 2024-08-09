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
from reverie.backend_server.maze import Maze
sys.path.append('../')

from global_methods import *

from persona.memory_structures.spatial_memory import *
from persona.memory_structures.associative_memory import *
from persona.memory_structures.scratch import *

from persona.cognitive_modules.retrieve import *
from persona.cognitive_modules.plan import *
from persona.cognitive_modules.reflect import *
from persona.cognitive_modules.execute import *
from persona.cognitive_modules.converse import *

class Agent: 
  def __init__(self, name, folder_mem_saved=False):
    # PERSONA BASE STATE 
    # <name> is the full name of the persona. This is a unique identifier for
    # the persona within Reverie. 
    self.name = name

    # PERSONA MEMORY 
    # If there is already memory in folder_mem_saved, we load that. Otherwise,
    # we create new memory instances. 
    # <s_mem> is the persona's spatial memory. 
    # Review Note:
    # Why is folder_mem_saved defaulted to a boolean and then used in a string
    # to access persona specific information if i understand correctly?
    f_s_mem_saved = f"{folder_mem_saved}/bootstrap_memory/spatial_memory.json"
    self.s_mem = MemoryTree(f_s_mem_saved)
    # <s_mem> is the persona's associative memory. 
    f_a_mem_saved = f"{folder_mem_saved}/bootstrap_memory/associative_memory"
    self.a_mem = AssociativeMemory(f_a_mem_saved)
    # <scratch> is the persona's scratch (short term memory) space. 
    scratch_saved = f"{folder_mem_saved}/bootstrap_memory/scratch.json"
    self.scratch = Scratch(scratch_saved)


  def save(self, save_folder): 
    """
    Save persona's current state (i.e., memory). 

    INPUT: 
      save_folder: The folder where we wil be saving our persona's state. 
    OUTPUT: 
      None
    """
    # Spatial memory contains a tree in a json format. 
    # e.g., {"double studio": 
    #         {"double studio": 
    #           {"bedroom 2": 
    #             ["painting", "easel", "closet", "bed"]}}}
    f_s_mem = f"{save_folder}/spatial_memory.json"
    self.s_mem.save(f_s_mem)
    
    # Associative memory contains a csv with the following rows: 
    # [event.type, event.created, event.expiration, s, p, o]
    # e.g., event,2022-10-23 00:00:00,,Isabella Rodriguez,is,idle
    f_a_mem = f"{save_folder}/associative_memory"
    self.a_mem.save(f_a_mem)

    # Scratch contains non-permanent data associated with the persona. When 
    # it is saved, it takes a json form. When we load it, we move the values
    # to Python variables. 
    f_scratch = f"{save_folder}/scratch.json"
    self.scratch.save(f_scratch)


  def perceive(self, maze:Maze)->list[ConceptNode]:
    """
    This function takes the current maze, and returns events that are 
    happening around the persona. 
    Importantly, perceive is guided by three key hyper-parameter for the  persona: 
    1) att_bandwidth
    2) vision_r
    3) retention. 

    First, <att_bandwidth> determines the number of nearby events that the 
    persona can perceive. Say there are 10 events that are within the vision
    radius for the persona -- perceiving all 10 might be too much. So, the 
    persona perceives the closest att_bandwidth number of events in case there
    are too many events. 

    Second, the persona does not want to perceive and think about the same 
    event at each time step. That's where <retention> comes in -- there is 
    temporal order to what the persona remembers. So if the persona's memory
    contains the current surrounding events that happened within the most 
    recent retention, there is no need to perceive that again. xx

    INPUT: 
      maze: Current <Maze> instance of the world. 
    OUTPUT: 
      a list of <ConceptNode> that are perceived and new. 
        See associative_memory.py -- but to get you a sense of what it 
        receives as its input: "s, p, o, desc, persona.scratch.curr_time"
    """
    def generate_poig_score(event_type:str, description:str): 
      if "is idle" in description: 
        return 1
      elif event_type == "event": 
        return run_gpt_prompt_event_poignancy(self, description)
      elif event_type == "chat": 
        return run_gpt_prompt_chat_poignancy(self, self.scratch.act_description)

    # PERCEIVE SPACE
    # We get the nearby tiles given our current tile and the persona's vision
    # radius. 
    # Review Note: scratch should not be managing these attributes
    nearby_tiles = maze.get_nearby_tiles(self.scratch.curr_tile, 
                                         self.scratch.vision_r)

    # We then store the perceived space. Note that the s_mem of the persona is
    # in the form of a tree constructed using dictionaries. 
    tree = self.s_mem.tree

    # PERCEIVE EVENTS. 
    # We will perceive events that take place in the same arena as the
    # persona's current arena. 
    curr_arena_path = maze.get_tile_path(self.scratch.curr_tile, "arena")
    # We will order our percept based on the distance, with the closest ones
    # getting priorities. 
    percept_events_list = []

    for tile in nearby_tiles: 
      tile_details = maze.access_tile(tile)
      tile_path = maze.get_tile_path(tile_details, "arena")
      world = tile_details["world"]
      sector = tile_details["sector"]
      arena = tile_details["arena"]
      game_object = tile_details["arena"]
      events = tile_details["events"]

      if (world and world not in tree): 
        tree[world] = {}
      if (sector and sector not in tree[world]): 
        tree[world][sector] = {}
      if (arena and arena not in tree[world][sector]): 
        tree[world][sector][arena] = []
      if (game_object and game_object not in tree[world][sector][arena]): 
        tree[world][sector][arena].append(game_object)

      if (events and tile_path == curr_arena_path):
        # This calculates the distance between the persona's current tile, 
        # and the target tile.
        dist = math.dist([tile_details[0], tile_details[1]], 
                         [self.scratch.curr_tile[0], 
                          self.scratch.curr_tile[1]])
        # Add any relevant events to our temp set/list with the distant info. 
        for event in events:
          if (dist,event) not in percept_events_list: 
            percept_events_list.append((dist, event))

    # We sort, and perceive only persona.scratch.att_bandwidth of the closest
    # events. If the bandwidth is larger, then it means the persona can perceive
    # more elements within a small area. 
    percept_events_list = sorted(percept_events_list, key=itemgetter(0))
    perceived_events = [event for _,event in percept_events_list[:self.scratch.att_bandwidth]]

    # Storing events. 
    # <ret_events> is a list of <ConceptNode> instances from the persona's 
    # associative memory. 
    ret_events:list[ConceptNode] = []
    for p_event in perceived_events: 
      s, p, o, desc = p_event
      if not p: 
        # If the object is not present, then we default the event to "idle".
        p = "is"
        o = "idle"
        desc = "idle"
      desc = f"{s.split(':')[-1]} is {desc}"
      p_event = (s, p, o)

      # We retrieve the latest persona.scratch.retention events. If there is  
      # something new that is happening (that is, p_event not in latest_events),
      # then we add that event to the a_mem and return it. 
      # Review Note:
      # Surely the same event cannot occur in two places, if this is the case, then why call this every time?
      latest_events = self.a_mem.get_summarized_latest_events(
                                      self.scratch.retention)
      if p_event not in latest_events:
        # We start by managing keywords. 
        keywords = set()
        if ":" in p_event[0]: 
          sub = p_event[0].split(":")[-1]
        else:
          sub = p_event[0]
        if ":" in p_event[2]: 
          obj = p_event[2].split(":")[-1]
        else:
          obj = p_event[2]
        keywords.update([sub, obj])

        # Get event embedding
        desc_embedding_in = desc
        if "(" in desc: 
          desc_embedding_in = (desc_embedding_in.split("(")[1]
                                                .split(")")[0]
                                                .strip())
        if desc_embedding_in in self.a_mem.embeddings: 
          event_embedding = self.a_mem.embeddings[desc_embedding_in]
        else: 
          event_embedding = get_embedding(desc_embedding_in)
        event_embedding_pair = (desc_embedding_in, event_embedding)
        
        # Get event poignancy. 
        event_poignancy = generate_poig_score("event", desc_embedding_in)

        # If we observe the persona's self chat, we include that in the memory
        # of the persona here. 
        chat_node_ids = []
        if p_event[0] == f"{self.name}" and p_event[1] == "chat with": 
          curr_event = self.scratch.act_event
          if self.scratch.act_description in self.a_mem.embeddings: 
            chat_embedding = self.a_mem.embeddings[self.scratch.act_description]
          else: 
            chat_embedding = get_embedding(self.scratch.act_description)
          chat_embedding_pair = (self.scratch.act_description, 
                                 chat_embedding)
          chat_poignancy = generate_poig_score("chat", self.scratch.act_description)
          chat_node = self.a_mem.add_chat(self.scratch.curr_time, None,
                        curr_event[0], curr_event[1], curr_event[2], 
                        self.scratch.act_description, keywords, 
                        chat_poignancy, chat_embedding_pair, 
                        self.scratch.chat)
          chat_node_ids = [chat_node.node_id]

        # Finally, we add the current event to the agent's memory. 
        ret_events += [self.a_mem.add_event(self.scratch.curr_time, None,
                             s, p, o, desc, keywords, event_poignancy, 
                             event_embedding_pair, chat_node_ids)]
        self.scratch.importance_trigger_curr -= event_poignancy
        self.scratch.importance_ele_n += 1

    return ret_events


  def retrieve(self, perceived):
    """
    This function takes the events that are perceived by the persona as input
    and returns a set of related events and thoughts that the persona would 
    need to consider as context when planning. 

    INPUT: 
      perceived: a list of event <ConceptNode>s that represent any of the events
      `         that are happening around the persona. What is included in here
                are controlled by the att_bandwidth and retention 
                hyper-parameters.
    OUTPUT: 
      retrieved: a dictionary of dictionary. The first layer specifies an event, 
                 while the latter layer specifies the "curr_event", "events", 
                 and "thoughts" that are relevant.
    """
    # We rerieve events and thoughts separately. 
    retrieved = dict()
    for event in perceived: 
      retrieved[event.description] = dict()
      retrieved[event.description]["curr_event"] = event
      
      relevant_events = self.a_mem.retrieve_relevant_events(
                          event.subject, event.predicate, event.object)
      retrieved[event.description]["events"] = list(relevant_events)

      relevant_thoughts = self.a_mem.retrieve_relevant_thoughts(
                            event.subject, event.predicate, event.object)
      retrieved[event.description]["thoughts"] = list(relevant_thoughts)
      
    return retrieved



  def plan(self, maze, personas, new_day, retrieved):
    """
    Main cognitive function of the chain. It takes the retrieved memory and 
    perception, as well as the maze and the first day state to conduct both 
    the long term and short term planning for the persona. 

    INPUT: 
      maze: Current <Maze> instance of the world. 
      personas: A dictionary that contains all persona names as keys, and the 
                Persona instance as values. 
      new_day: This can take one of the three values. 
        1) <Boolean> False -- It is not a "new day" cycle (if it is, we would
           need to call the long term planning sequence for the persona). 
        2) <String> "First day" -- It is literally the start of a simulation,
           so not only is it a new day, but also it is the first day. 
        2) <String> "New day" -- It is a new day. 
      retrieved: dictionary of dictionary. The first layer specifies an event,
                 while the latter layer specifies the "curr_event", "events", 
                 and "thoughts" that are relevant.
    OUTPUT 
      The target action address of the persona (persona.scratch.act_address).
    """
    return plan(self, maze, personas, new_day, retrieved)


  def execute(self, maze, personas, plan):
    """
    This function takes the agent's current plan and outputs a concrete 
    execution (what object to use, and what tile to travel to). 

    INPUT: 
      maze: Current <Maze> instance of the world. 
      personas: A dictionary that contains all persona names as keys, and the 
                Persona instance as values. 
      plan: The target action address of the persona  
            (persona.scratch.act_address).
    OUTPUT: 
      execution: A triple set that contains the following components: 
        <next_tile> is a x,y coordinate. e.g., (58, 9)
        <pronunciatio> is an emoji.
        <description> is a string description of the movement. e.g., 
        writing her next novel (editing her novel) 
        @ double studio:double studio:common room:sofa
    """
    return execute(self, maze, personas, plan)


  def reflect(self):
    """
    Reviews the persona's memory and create new thoughts based on it. 

    INPUT: 
      None
    OUTPUT: 
      None
    """
    reflect(self)


  def move(self, maze, personas, curr_tile, curr_time):
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
    # Updating persona's scratch memory with <curr_tile>. 
    self.scratch.curr_tile = curr_tile

    # We figure out whether the persona started a new day, and if it is a new
    # day, whether it is the very first day of the simulation. This is 
    # important because we set up the persona's long term plan at the start of
    # a new day. 
    new_day = False
    if not self.scratch.curr_time: 
      new_day = "First day"
    elif (self.scratch.curr_time.strftime('%A %B %d')
          != curr_time.strftime('%A %B %d')):
      new_day = "New day"
    self.scratch.curr_time = curr_time

    # Main cognitive sequence begins here. 
    perceived = self.perceive(maze)
    retrieved = self.retrieve(perceived)
    plan = self.plan(maze, personas, new_day, retrieved)
    self.reflect()

    # <execution> is a triple set that contains the following components: 
    # <next_tile> is a x,y coordinate. e.g., (58, 9)
    # <pronunciatio> is an emoji. e.g., "\ud83d\udca4"
    # <description> is a string description of the movement. e.g., 
    #   writing her next novel (editing her novel) 
    #   @ double studio:double studio:common room:sofa
    return self.execute(maze, personas, plan)


  def open_convo_session(self, convo_mode): 
    open_convo_session(self, convo_mode)
    




































