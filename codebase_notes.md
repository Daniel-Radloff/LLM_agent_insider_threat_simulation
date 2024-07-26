# Notes on this code base structure
I would like to just note that: everyone is learning. I'm also not a python specific dev and I have little professional dev experience and that's ok. These are just critiques and suggestions and are not meant to hurt or belittle anyone :). Rather show how to improve and get better. Critique can sometimes feel harsh, however It's important to take them in the spirit that they are meant. They are an opportunity to improve. Without this basis, I would never have been able to complete my research. I thank the creators for contributing in the name of open source research.
## Suggested Modifications
- restructure static assets and shared stuff, because the current project directory structure is very odd.
## Original Filtered Directory Structure
```
.
├── environment
│   └── frontend_server
│       ├── frontend_server
│       │   ├── __init__.py
│       │   ├── settings
│       │   │   ├── base.py
│       │   │   ├── __init__.py
│       │   │   └── local.py
│       │   ├── urls.py
│       │   ├── utils.py
│       │   └── wsgi.py
│       ├── global_methods.py
│       ├── manage.py
│       ├── templates
│       │   ├── demo
│       │   ├── home
│       │   ├── landing
│       │   ├── path_tester
│       │   └── persona_state
│       ├── temp_storage
│       └── translator
│           ├── admin.py
│           ├── apps.py
│           ├── __init__.py
│           ├── migrations
│           │   ├── 0001_initial.py
│           │   ├── 0002_evaldata_target_agent.py
│           │   ├── 0003_auto_20230327_0851.py
│           │   ├── 0004_auto_20230330_0204.py
│           │   ├── 0005_delete_evaldata.py
│           │   └── __init__.py
│           ├── models.py
│           ├── tests.py
│           └── views.py
└── reverie
    ├── backend_server
    │   ├── global_methods.py
    │   ├── maze.py
    │   ├── path_finder.py
    │   ├── persona
    │   │   ├── cognitive_modules
    │   │   │   ├── converse.py
    │   │   │   ├── execute.py
    │   │   │   ├── perceive.py
    │   │   │   ├── plan.py
    │   │   │   ├── reflect.py
    │   │   │   └── retrieve.py
    │   │   ├── memory_structures
    │   │   │   ├── associative_memory.py
    │   │   │   ├── scratch.py
    │   │   │   └── spatial_memory.py
    │   │   ├── persona.py
    │   │   └── prompt_template
    │   │       ├── defunct_run_gpt_prompt.py
    │   │       ├── gpt_structure.py
    │   │       ├── print_prompt.py
    │   │       ├── run_gpt_prompt.py
    │   │       ├── safety
    │   │       ├── v1
    │   │       ├── v2
    │   │       └── v3_ChatGPT
    │   ├── reverie.py
    │   ├── test.py
    │   └── utils.py
    ├── compr sets an event to null.ess_sim_storage.py
    └── global_methods.py
```
## Common Files
`global_methods.py` is a repeated file, it has the same content each time and just defines some methods the author likes to use in the code base:
These functions are for the most part never used?
- `create_folder_if_not_there`
- `check_if_file_exists`
- `find_filenames`: `find` like implementation
- `copyanything`: under dirs, not a move
- `get_row_len`: get row length of a CSV
- `write_list_of_list_to_csv`: standardized format for writing to csv, *multiple lines/2D list*
- `write_list_to_csv`: standardized format for writing to csv, *one line/1D list*
- `read_file_to_list`: read standardized format to list, entire file
- `read_file_to_set`: read standardized format, read *column* of entire file to (`numpy`?) set
- `average`: on list
- `std`: standard deviation on list

## Reverie
Reverie is the main code for Agents themselves.

### Main Directory
Majority of code is contained under backend_server directory

#### compress_sim_storage.py
This "compresses", the results of a simulation into the `environment/frontend_server/compressed_storage` directory, it is unclear why this is under the backend side of things and not the frontend side as there are no methods from backend and simulations seem to be largely related to the front end. The methods only seem to be used inside the file itself. It is unclear how this works.

### backed_server
Ignore `global_methods.py` and `test.py`

#### utils.py
Untracked user generated file that specifies some constants, we won't use API key, so this could just be public.
Weirdly again this files defaults go back into the `environment/frontend_server` directory.

#### maze.py
This is the map. Provides an interface and view for the agent to interact with the map (Maze class).
##### Maze Class
- `__init__(maze_name)`: reads a bunch of information about the map. Also reads in the map data and initializes all the stuff to interact with the map. It defines a few key attributes:
    - `name`, `width`, and `height`.
    - `sq_title_size`: the pixel height/width of a tile, which is kinda weird thing to define in backend.
    - `special_constraint`: "String description of any relevant special constraints world may have"
    - `collision_maze`: **Note: refactored** into a local variable
    - `tiles`: maps co-ordinates to world points and attaches meaningful information to those points'
    - `address_tiles`: provides the inverse of `tiles`
- `turn_coordinate_to_tile(px_coordiante)`: 2 parameter tuple of pixel co-ordinates, turn it into game space co-ordinates.
- `access_tile`: return key-value pairs of information about tile at an x, y position. Uses `Maze.self.tiles`. 
- `get_tile_path`: return string address of tile from x, y position and level specification (not sure about level specification or what that means or how its used yet?).
- `get_nearby_tiles`: returns all tiles in view of the agent at a position
- `add_event_from_tile`: weird name, adds an event tuple to a tile, in the doc string it says event triple? *in the `Maze.__init__`, events had 4 attributes, this is sus!* (it is most likely 4 parameters)
- `remove_event_from_tile`: removes an event associated with a tile
- `turn_event_from_tile_idle`: sets an event to null.
- `remove_subject_events_from_tile`: I have no idea.
#### reverie.py
This contains the main for the 'backend'. For the program, you give it a base simulation to start from, and then you give it a name of an output to generate.
The weird thing about this implementation is that the back and forth between the frontend and backend happens through the file system. Not even on some virtual disk. This should most likely be reimplemented into an in memory implementation. Hitting the disk this much is just going to fry my system for the duration of simulations I want to run.
The frontend stores the state of the world as well? Which is strange. These discrepancies need to be refactored to create more readable and standardized implementation.
##### Reverie Class
- `__init__(fork_sim_code,sim_code)`: well documented
    - `fork_sim_code`, `sim_code`: these reference directory names in the location defined in `utils.fs_storage`.
    - `start_time`,`curr_time`: is this the virtual start time or other? not sure.
    - `maze`: the maze class for this simulation
    - `sec_per_step`: number of seconds each step in game takes.
    - `step`: number of tiles personas have moved? *(what if multiple and one doesn't?!??!?! not sure.)*
    - `personas`: all the personas
    - `personas_tiles`: the game co-ordinates of the personas
    - `server_sleep`: Used somewhere in the main server loop, I suspect this is so that the disk doesn't get fried.
- `save`: saves the current state of the simulation (metadata and personas)
    - first metadata is saved
    - calls to `Persona.save(save_folder)`
- `start_path_tester_server`: not entirely sure what this does on a first look, most likely generates some kind of way for the agents to learn the map.
- `start_server(int_counter)`: `int_counter` stores the number of steps to take for this run.
- `open_server`: provides an interactive command line for the server.
#### path_finder.py
Most of this file needs to be reimplemented because its very inefficient.
- `path_finder_v2`: a path finding algorithm.
- `path_finder`: this is the public facing function, it just moves a few things and then sends it off to the `path_finder_v2` function.

### backend_server/persona
This is a difficult to follow in its current state, but here is the main summary:
Persona.py is the main controller of everything under `/persona` and its the main high level abstraction used for all agent interactions.
There are 3 directories:
- `cognitive_modules`: this stores some functions that are used in the `Persona` class, *this should be completely reworked so that all these little functions are encapsulated in the class instead of like this.*
- `memory_structures`: this stores 3 classes, scratch (short term memory), associative_memory, and spatial_memory, each serve a specific task.
#### persona.py
"Defines persona class that powers the agents."
There are a bunch of `import *`'s which is gonna make things a bit more tedious to find where stuff is coming from.
- `__init__(name,folder_mem_saved)`:
    - `folder_mem_saved` is only ever initialized as a string, so this has to be a mistake.
    - the initialization of the rest of the variables are shoddy with how it handles files not existing, such as the creation of a new persona, will look at the README again later to check if I'm missing something.

### backend_server/persona_memory_structures
#### spatial_memory.py
Defines the `MemoryTree` class that contains spatial memory and "aids in grounding their behavior in the game world".

### prompt_template
#### run_gpt_prompt.py
- `run_gpt_promp_event_poignancy(persona, event_description, test_input=None, verbose=False)`
  In the file poignancy_event_v1.txt, the prompt is something along the lines of:
  ```
  On the scale of 1 to 10, where 1 is purely mundane
  (e.g., brushing teeth, making bed) and 10 is
  extremely poignant (e.g., a break up, college
  acceptance), rate the likely poignancy of the
  following piece of memory.
  Memory: buying groceries at The Willows Market
  and Pharmacy
  Rating: <fill in>
  ```
however, this doesn't make sense because if something is poignant then it means it's sad, but college acceptance is not sad. Furthermore, in the paper, it is the section under importance, not strictly sad events. Therefor: I think this is a mistake and what is meant to happen here is rank the events on impact/importance on the agents' life.
