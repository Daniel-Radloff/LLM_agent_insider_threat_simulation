# Notes on this code base structure
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
    ├── compress_sim_storage.py
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

#### reverie.py

#### path_finder.py
