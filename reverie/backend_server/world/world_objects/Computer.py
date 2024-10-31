from typing import Union, List, Dict
from reverie.backend_server.world.world_objects.WorldObject import WorldObject

class Computer(WorldObject):
  '''
    A computer that an agent can interact with. It includes a simulated drive with different files and devices.
  '''
  def __init__(self, object_id: str, data: dict) -> None:
    super().__init__(object_id, data)
    self.drive = data['drives']  # A dictionary representing the drive, e.g., {"C:": ["file1.txt", "file2.exe"]}
    self.devices = data['devices']  # List of devices attached to the computer, e.g., ["printer", "mouse"]
    self.screen = "Desktop"  # Initial screen display, representing what is currently shown on the screen

  def list_files(self, drive_letter: str) -> str:
    ''' List the files in a specified drive. '''
    if drive_letter in self.drive:
      files = "\n".join(self.drive[drive_letter])
      self.screen = f'Files in {drive_letter}:\n{files}'  # Update the screen display
      return self.screen
    return f'Drive {drive_letter} not found.'

  def access_file(self, drive_letter: str, file_name: str) -> str:
    ''' Access a specific file from a drive. '''
    if drive_letter in self.drive and file_name in self.drive[drive_letter]:
      self.screen = f'You are viewing the file: {file_name} from {drive_letter}'  # Update the screen display
      return self.screen
    return f'File "{file_name}" not found in drive {drive_letter}.'

  def list_devices(self) -> str:
    ''' List the devices connected to the computer. '''
    if self.devices:
      devices_list = "\n".join(self.devices)
      self.screen = f'Connected devices:\n{devices_list}'  # Update the screen display
      return self.screen
    return 'No devices connected.'

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

    # Parse the input command
    command_parts = input.split()
    command = command_parts[0]

    if command == "list_files" and len(command_parts) == 2:
      return self.list_files(command_parts[1])
    elif command == "access_file" and len(command_parts) == 3:
      return self.access_file(command_parts[1], command_parts[2])
    elif command == "list_devices":
      return self.list_devices()
    else:
      return f'Unknown command: {input}'
