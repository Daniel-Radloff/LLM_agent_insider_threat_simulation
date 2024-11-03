from typing import Union, List, Dict
from reverie.backend_server.world.world_objects.WorldObject import WorldObject
import copy

class DiskDrive():
  '''
  Some bulk storage device that a computer has access to. 
  It can be on a network or somewhere else.
  For clarity, this object keeps its own logs, however other
  objects are free to derive their own logs from interactions
  with this device.
  '''
  def __init__(self, structure: Dict) -> None:
    self.structure = structure  # The drive structure containing folders and files
    self.current_path = []  # Keeps track of the current path

  def execute(self,action:str):
    command = action.split(' ')
    match command[0]:
      case "ls":
        return self.list_directory(None if len(command) == 1 else command[1])
      case "cd":
        if len(command) == 2:
          return self.change_directory(command[1])
        else:
          return "Usage: cd <directory>"
      case "touch":
        if len(command) == 2:
          return self.add_file(command[1])
        else:
          return "Usage: touch <file_name>, no spaces allowed for file names"
      case "mkdir":
        if len(command) == 2:
          return self.add_folder(command[1])
        else:
          return "Usage: mkdir <dir_name>, no spaces allowed for directory names"
      case "open":
        if len(command) == 2:
          return self.open_file(command[1])
        else:
          return "Usage: open <file_name>"
      case "cp":
        if len(command) == 3:
          return self.copy_file(command[1], command[2])
        else:
            return "Usage: cp <file/dir name> <new location>, no spaces allowed for paths or names"
      case "mv":
        if len(command) == 3:
          return self.move_file(command[1], command[2])
        else:
          return "Usage: mv <file/dir name> <new location>, no spaces allowed for paths or names"
      case "rm":
        if len(command) == 2:
          return self.delete_file(command[1])
        else:
          return "Usage: rm <file>"
      case "rm -rf":
        if len(command) == 2:
          return self.delete_folder(command[1])
        else:
          return "Usage: rm -rf <directory>"
      case _:
        raise ValueError(f"No supported operation for Disk found, command: '{" ".join(command)}' not supported")

  @property
  def availible_actions(self):
    return '\n'.join([
        "Disk Operations",
        "ls - lists the contents in the current directory",
        "cd <directory> - change to a given directory",
        "touch <file_name> - create a new file with a given name",
        "mkdir <dir_name> - create a new directory with given name",
        "open - open file in default editor to view and modify contents",
        "cp <file/dir name> <new location> - copy a directory or file, must use full path for target",
        "mv <file/dir name> <new location> - move a directory or file, must use full path for target",
        "rm <file> - remove a file",
        "rm -rf <directory> - remove a directory",
      ])

  def _get_directory(self, path: List[str]) -> Dict:
    '''
    Internal method to retrieve a directory based on the current path.
    '''
    directory = self.structure
    try:
      for folder in path:
        if isinstance(directory[folder],dict):
          directory = directory[folder]
        else:
          raise ValueError(f'"{path[-1]}" is a file, not a directory.')
    except KeyError:
      raise ValueError(f'Path not found: {"/".join(path)}')
    return directory

  def _resolve_path(self,current_directory: List[str], target_directory: str) -> List[str]:
    # if full path
    if target_directory[0] == "/":
      full_path = target_directory.split('/')
    else:
      full_path = [*current_directory,*target_directory.split('/')]
    resolved_path = []
    for name in full_path:
      if name == '..':
        if resolved_path:
          resolved_path.pop()
      else:
        resolved_path.append(name)
    # pop last so that original code logic remains unchanged.
    resolved_path.pop()
    return resolved_path

  def list_directory(self,optional_target:Union[None,str]=None) -> str:
    ''' List the contents of the current directory. '''
    try:
      if optional_target is not None:
        resolved_path = self._resolve_path(self.current_path, optional_target)
      else:
        resolved_path = self.current_path
      directory = self._get_directory(resolved_path)
      contents = "\n".join(directory.keys())
      return f'Contents of directory {"/".join(resolved_path)}:\n{contents}'
    except ValueError as e:
      return str(e)

  def change_directory(self, folder_name: str) -> str:
    ''' Change the current directory to a specified folder. '''
    try:
      resolved_path = self._resolve_path(self.current_path, folder_name)
      _ = self._get_directory(resolved_path)
      resolved_path.append(folder_name)
      self.current_path = resolved_path 
      return f'Changed directory to: {"/".join(self.current_path)}'
    except ValueError as e:
      return str(e)

  def add_file(self, file_name: str) -> str:
    ''' Add a file to the current directory. '''
    try:
      resolved_path = self._resolve_path(self.current_path, file_name)
      directory = self._get_directory(resolved_path)
      directory[file_name] = ""
      return f'File "{file_name}" added to {"/".join(resolved_path)}.'
    except ValueError as e:
      return str(e)

  def add_folder(self, folder_name: str) -> str:
    ''' Add a folder to the current directory. '''
    try:
      resolved_path = self._resolve_path(self.current_path, folder_name)
      directory = self._get_directory(resolved_path)
      directory[folder_name] =  {}
      return f'Folder "{folder_name}" added to {"/".join(resolved_path)}.'
    except ValueError as e:
      return str(e)

  def get_current_path(self) -> str:
    ''' Get the current path as a string. '''
    return "/".join(self.current_path) or "/"

  def copy_file(self, file_name: str, dest_path: str) -> str:
    ''' Copy a file from the current directory to another directory. '''
    resolved_source_path = self._resolve_path(self.current_path, file_name)
    resolved_dest_path = self._resolve_path(self.current_path, dest_path)
    try:
      # Get the current directory and destination directory
      source_directory = self._get_directory(resolved_source_path)
      dest_directory = self._get_directory(resolved_dest_path)
      
      # Copy the file
      dest_directory[file_name] = copy.deepcopy(source_directory[file_name])
      return f'File/Directory "{file_name}" copied to {"/".join(dest_path)}.'
    except KeyError:
      return f'File "{file_name}" does not exist in the current directory: {"/".join(resolved_source_path)}.'
    except ValueError as e:
      return str(e)

  def move_file(self, file_name: str, dest_path: str) -> str:
    ''' Move a file from the current directory to another directory. '''
    resolved_source_path = self._resolve_path(self.current_path, file_name)
    resolved_dest_path = self._resolve_path(self.current_path, dest_path)
    try:
      # Get the current directory and destination directory
      source_directory = self._get_directory(resolved_source_path)
      dest_directory = self._get_directory(resolved_dest_path)
      
      # Copy the file
      dest_directory[file_name] = source_directory.pop(file_name)
      return f'File/Directory "{file_name}" moved to {"/".join(dest_path)}.'
    except KeyError:
      return f'File "{file_name}" does not exist in the current directory: {"/".join(resolved_source_path)}.'
    except ValueError as e:
      return str(e)

  def delete_file(self, file_name: str) -> str:
    ''' Delete a file from the current directory. '''
    resolved_path = self._resolve_path(self.current_path, file_name)
    try:
      directory = self._get_directory(resolved_path)
      # Delete the file
      del directory[file_name]
      return f'File "{file_name}" deleted from {"/".join(resolved_path)}.'
    except KeyError:
      return f'File "{file_name}" does not exist in the current directory: {"/".join(resolved_path)}.'
    except ValueError as e:
        return str(e)

  def delete_folder(self, folder_name: str) -> str:
    ''' Delete a folder from the current directory. '''
    return self.delete_file(folder_name)

  def open_file(self,file_name:str) -> str:
    resolved_path = self._resolve_path(self.current_path, file_name)
    try:
      directory = self._get_directory(resolved_path)
      file_contents = directory[file_name]
      return f'{file_name}:\n{file_contents}'
    except KeyError:
      return f'File "{file_name}" does not exist in the current directory: "{"/".join(resolved_path)}"'
    except ValueError as e:
      return str(e)

# Example usage
drive_structure = {
    "C:": {
      "file1.txt" : "data here",
      "file2.docx" : "plain text in the document",
      "Projects": {
        "project1.xlxs": "some data",
        "project2.xlxs": "other data"
      },
      "Reports": {
        "report1.pdf" : "text contained in the pdf",
        "report2.pdf": "plain text aswell"
      },
    },
    "D:": {
      "game.iso" : "some description of what it contains"
    }
}

class Computer(WorldObject):
  '''
    A computer that an agent can interact with. It includes a simulated drive with different files and devices.
  '''
  def __init__(self, object_id: str, data: dict) -> None:
    super().__init__(object_id, data)
    self.drive = DiskDrive(data['drives'])

  def interact(self, input: Union[str, None] = None) -> str:
    '''
      Interact with the computer. Commands can be:
      - "list_files <drive_letter>"
      - "access_file <drive_letter> <file_name>"
      - "list_devices"
    '''
    if input is None:
      # Return the current screen display when no input is given
      return f'On the computer screen you read: {self.screen}'

    # handle commands
    try:
      self.screen = self.drive.execute(input)
    except ValueError as e:
      print(e)
    message = f"No viable device found for command: {input}"
    print(message)
    message = message + '\n' + self.drive.availible_actions
    return message
