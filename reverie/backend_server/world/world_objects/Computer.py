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

# Note: deadlines are really bad for writing passable code. I have sympathy for the original authors

class Email:
  '''
  The LLM realllllly wants to use something that can check emails so we kinda need some mock system to satiate it.
  '''
  def __init__(self, structure: Dict) -> None:
    # Email structure will include inbox, sent, and drafts
    self.structure = structure
    self.current_folder = 'inbox'  # Default to inbox

  def add_email(self):
    '''
    so we can send them emails.
    '''
    raise NotImplementedError()

  def execute(self, action: str):
    command = action.split(' ',2)
    match command[0]:
      case "view_inbox":
        return self.view_inbox()
      case "view_sent":
        return self.view_sent()
      case "view_drafts":
        return self.view_drafts()
      case "read":
        if len(command) == 2:
          return self.read_email(command[1])
        else:
          return "Usage: read <email_id>"
      case "compose":
        if len(command) == 3:
          recipient = command[1]
          subject = " ".join(command[2:])
          return self.compose_email(recipient, subject)
        else:
          return "Usage: compose <recipient> <subject>"
      case "send_draft":
        if len(command) == 2:
          return self.send_draft(command[1])
        else:
          return "Usage: send_draft <draft_id>"
      case "delete":
        if len(command) == 2:
          return self.delete_email(command[1])
        else:
          return "Usage: delete <email_id>"
      case "edit_draft":
        if len(command) == 3:
          draft_id = command[1]
          body = command[2]
          return self.edit_draft(draft_id, body)
        else:
          return "Usage: edit_draft <draft_id> <new_body>"
      case _:
        return f"Command not supported: {action}"

  @property
  def available_actions(self):
    return '\n'.join([
      "Email Operations:",
      "view_inbox - view all emails in the inbox",
      "view_sent - view all emails in the sent folder",
      "view_drafts - view saved drafts",
      "read <email_id> - read an email",
      "compose <recipient> <subject> - create a new email and save it as a draft",
      "edit_draft <draft_id> <new_body> - replace the body/message of a draft with new text",
      "send_draft <draft_id> - send an email from the drafts",
      "delete <email_id> - delete an email"
      ])

  def view_inbox(self) -> str:
    ''' List the emails in the inbox. '''
    inbox = self.structure.get('inbox', [])
    if not inbox:
      return "Inbox is empty."
    return "Inbox:\n" + "\n".join(f"{i}: {email['subject']}" for i, email in enumerate(inbox))

  def view_sent(self) -> str:
    ''' List the emails in the sent folder. '''
    sent = self.structure.get('sent', [])
    if not sent:
      return "Sent folder is empty."
    return "Sent Emails:\n" + "\n".join(f"{i}: {email['subject']}" for i, email in enumerate(sent))

  def view_drafts(self) -> str:
    ''' List the emails saved as drafts. '''
    drafts = self.structure.get('drafts', [])
    if not drafts:
      return "No drafts available."
    return "Drafts:\n" + "\n".join(f"{i}: To {draft['to']}, Subject: {draft['subject']}" for i, draft in enumerate(drafts))

  def edit_draft(self, draft_id: str, body: str) -> str:
    '''
    Edit the body of an existing draft email by its ID.
    '''
    try:
        draft = self.structure['drafts'][int(draft_id)]
        draft['body'] = body
        return f"Draft ID {draft_id} updated. New body: {body}"
    except (IndexError, ValueError):
      return f"Draft ID {draft_id} not found. Current drafts availible:\n{self.view_drafts()}"

  def read_email(self, email_id: str) -> str:
    ''' Read the content of an email from the inbox. '''
    try:
      email = self.structure['inbox'][int(email_id)]
      return f"From: {email['from']}\nTo: {email['to']}\nSubject: {email['subject']}\n\n{email['body']}"
    except (IndexError, ValueError):
      return f"Email ID {email_id} not found in the inbox."

  def compose_email(self, recipient: str, subject: str) -> str:
    ''' Compose a new email and save it as a draft. '''
    draft = {
        "from": "user@example.com",
        "to": recipient,
        "subject": subject,
        "body": "Empty"  # Placeholder body
    }
    self.structure['drafts'].append(draft)
    return f"Draft saved. To: {recipient}, Subject: {subject}.\nPlease edit the draft using 'edit_draft' to add your message."

  def send_draft(self, draft_id: str) -> str:
    ''' Send a draft email and move it to the sent folder. '''
    try:
      draft = self.structure['drafts'].pop(int(draft_id))
      self.structure['sent'].append(draft)
      return f"Mail sent to {draft['to']} with subject '{draft['subject']}'."
    except (IndexError, ValueError):
      return f"Draft ID {draft_id} not found."

  def delete_email(self, email_id: str) -> str:
    ''' Delete an email from the inbox. '''
    try:
      self.structure['inbox'].pop(int(email_id))
      return f"Email ID {email_id} deleted from inbox."
    except (IndexError, ValueError):
      return f"Email ID {email_id} not found in inbox."


class Computer(WorldObject):
  '''
    A computer that an agent can interact with. It includes a simulated drive with different files and devices.
  '''
  def __init__(self, object_id: str, data: dict) -> None:
    super().__init__(object_id, data)
    self.drive = DiskDrive(data['drives'][0])
    self.email = Email(data['email'])

  @property
  def availible_actions(self):
    # TODO needs more complex handling of state for login's etc
    if self.status != "Powered off":
      availible_commands = [
          self.drive.availible_actions,
          self.email.available_actions
        ]
      return '\n'.join(availible_commands)
    else:
      return 'Turn on' 

  def interact(self, input: Union[str, None] = None) -> str:
    if input is None:
      # Return the current screen display when no input is given
      return f'On the computer screen you read: {self.screen}'

    # handle commands
    if self.status == "Powered off":
      if input == "Turn on":
        self._status = "Powered on"
        return "computer is powering on"
      else:
        return f"Command {input} is not part of the availible commands:\n{self.availible_actions}"

    try:
      self.screen = self.drive.execute(input)
      return self.screen
    except ValueError as e:
      print(e)

    try:
      self.screen = self.email.execute(input)
      return self.screen
    except ValueError as e:
      print(e)

    message = f"No viable device found for command: {input}"
    print(message)
    message = message + '\n' + self.availible_actions
    return message
