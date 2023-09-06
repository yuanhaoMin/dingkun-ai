from .utils import merge_deltas, parse_partial_json
from .message_block import MessageBlock
from .code_block import CodeBlock
from .code_interpreter import CodeInterpreter

import os
import time
import json
import platform
import openai
import getpass
import requests
import readline
import urllib.parse
import tokentrim as tt
from rich import print
from rich.markdown import Markdown
from rich.rule import Rule

# Function schema for gpt-4
function_schema = {
  "name": "run_code",
  "description":
  "Executes code on the user's machine and returns the output",
  "parameters": {
    "type": "object",
    "properties": {
      "language": {
        "type": "string",
        "description":
        "The programming language",
        "enum": ["python", "shell", "applescript", "javascript", "html"]
      },
      "code": {
        "type": "string",
        "description": "The code to execute"
      }
    },
    "required": ["language", "code"]
  },
}

# Message for when users don't have an OpenAI API key.
missing_api_key_message = """> OpenAI API key not found

To use `GPT-4` (recommended) please provide an OpenAI API key.

To use `Code-Llama` (free but less capable) press `enter`.
"""

confirm_mode_message = """
**Open Interpreter** will require approval before running code. Use `interpreter -y` to bypass this.

Press `CTRL-C` to exit.
"""


class Interpreter:

  def __init__(self):
    self.messages = []
    self.temperature = 0.001
    self.api_key = None
    self.auto_run = False
    self.local = False
    self.model = "gpt-4"
    self.debug_mode = True

    # Get default system message
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'system_message.txt'), 'r') as f:
      self.system_message = f.read().strip()

    # Store Code Interpreter instances for each language
    self.code_interpreters = {}

    # No active block to start
    # (blocks are visual representation of messages on the terminal)
    self.active_block = None

    # Note: While Open Interpreter can use Llama, we will prioritize gpt-4.
    # gpt-4 is faster, smarter, can call functions, and is all-around easier to use.
    # This makes gpt-4 better aligned with Open Interpreters priority to be easy to use.
    pass


  def get_info_for_system_message(self):
    """
    Gets relevant information for the system message.
    """

    info = ""

    # Add user info
    username = getpass.getuser()
    current_working_directory = os.getcwd()
    operating_system = platform.system()

    info += f"\n\n[User Info]\nName: {username}\nCWD: {current_working_directory}\nOS: {operating_system}"

    if not self.local:

      # Open Procedures is an open-source database of tiny, structured coding tutorials.
      # We can query it semantically and append relevant tutorials/procedures to our system message:

      # Use the last two messages' content or function call to semantically search
      query = []
      for message in self.messages[-2:]:
        message_for_semantic_search = {"role": message["role"]}
        if "content" in message:
          message_for_semantic_search["content"] = message["content"]
        if "function_call" in message and "parsed_arguments" in message["function_call"]:
          message_for_semantic_search["function_call"] = message["function_call"]["parsed_arguments"]
        query.append(message_for_semantic_search)

      # Use them to query Open Procedures
      url = "https://open-procedures.replit.app/search/"

      try:
        relevant_procedures = requests.get(url, data=json.dumps(query)).json()["procedures"]
        info += "\n\n# Recommended Procedures\n" + "\n---\n".join(
          relevant_procedures) + "\nIn your plan, include steps and, if present, **EXACT CODE SNIPPETS** (especially for deprecation notices, **WRITE THEM INTO YOUR PLAN -- underneath each numbered step** as they will VANISH once you execute your first line of code, so WRITE THEM DOWN NOW if you need them) from the above procedures if they are relevant to the task. Again, include **VERBATIM CODE SNIPPETS** from the procedures above if they are relevant to the task **directly in your plan.**"
      except:
        # For someone, this failed for a super secure SSL reason.
        # Since it's not strictly necessary, let's worry about that another day. Should probably log this somehow though.
        pass

    elif self.local:
      pass

    return info

  def reset(self):
    self.messages = []
    self.code_interpreters = {}

  def load(self, messages):
    self.messages = messages

  def chat(self, message=None, return_messages=False):

    # Connect to an LLM (an large language model)
    if not self.local:
      # gpt-4
      self.verify_api_key()

    # ^ verify_api_key may set self.local to True, so we run this as an 'if', not 'elif':
    if self.local:
      pass

    # Display welcome message
    welcome_message = ""

    if self.debug_mode:
      welcome_message += "> Entered debug mode"

    # If self.local, we actually don't use self.model
    # (self.auto_run is like advanced usage, we display no messages)
    if not self.local and not self.auto_run:
      welcome_message += f"\n> Model set to `{self.model.upper()}`\n\n**Tip:** To run locally, use `interpreter --local`"

    # If not auto_run, tell the user we'll ask permission to run code
    # We also tell them here how to exit Open Interpreter
    if not self.auto_run:
      welcome_message += "\n\n" + confirm_mode_message

    welcome_message = welcome_message.strip()

    # Print welcome message with newlines on either side (aesthetic choice)
    # unless we're starting with a blockquote (aesthetic choice)
    if welcome_message != "":
      if welcome_message.startswith(">"):
        print(Markdown(welcome_message), '')
      else:
        print('', Markdown(welcome_message), '')

    # Check if `message` was passed in by user
    if message:
      # If it was, we respond non-interactively
      self.messages.append({"role": "user", "content": message})
      self.respond()

    if return_messages:
      return self.messages

  def verify_api_key(self):
    """
    Makes sure we have an OPENAI_API_KEY.
    """

    if self.api_key == None:

      if 'OPENAI_API_KEY' in os.environ:
        self.api_key = os.environ['OPENAI_API_KEY']
      else:
        # This is probably their first time here!
        print('', Markdown("**Welcome to Open Interpreter.**"), '')
        time.sleep(1)

        print(Rule(style="white"))

        print(Markdown(missing_api_key_message), '', Rule(style="white"), '')
        response = input("OpenAI API key: ")

        if response == "":
          pass
        else:
          self.api_key = response
          print('', Markdown(
            "**Tip:** To save this key for later, run `export OPENAI_API_KEY=your_api_key` on Mac/Linux or `setx OPENAI_API_KEY your_api_key` on Windows."),
                '')
          time.sleep(2)
          print(Rule(style="white"))

    openai.api_key = self.api_key

  def end_active_block(self):
    if self.active_block:
      self.active_block.end()
      self.active_block = None

  def respond(self):
    # Add relevant info to system_message
    # (e.g. current working directory, username, os, etc.)
    info = self.get_info_for_system_message()
    system_message = self.system_message + "\n\n" + info

    messages = tt.trim(self.messages, self.model, system_message=system_message)
    if self.debug_mode:
      print("\n", "Sending `messages` to LLM:", "\n")
      print(messages)
      print()

    # Make LLM call
    if not self.local:
      response = openai.ChatCompletion.create(
        model=self.model,
        messages=messages,
        functions=[function_schema],
        stream=True,
        temperature=self.temperature,
      )

    else:
      pass

    # Initialize message, function call trackers, and active block
    self.messages.append({})
    in_function_call = False
    llama_function_call_finished = False
    self.active_block = None

    for chunk in response:

      delta = chunk["choices"][0]["delta"]

      # Accumulate deltas into the last message in messages
      self.messages[-1] = merge_deltas(self.messages[-1], delta)

      # Check if we're in a function call
      if not self.local:
        condition = "function_call" in self.messages[-1]
      elif self.local:
        pass

      if condition:
        # We are in a function call.

        # Check if we just entered a function call
        if in_function_call == False:

          # If so, end the last block,
          self.end_active_block()

          # Print newline if it was just a code block or user message
          # (this just looks nice)
          last_role = self.messages[-2]["role"]
          if last_role == "user" or last_role == "function":
            print()

          # then create a new code block
          self.active_block = CodeBlock()

        # Remember we're in a function_call
        in_function_call = True

        # Now let's parse the function's arguments:

        if not self.local:
          # gpt-4
          # Parse arguments and save to parsed_arguments, under function_call
          if "arguments" in self.messages[-1]["function_call"]:
            arguments = self.messages[-1]["function_call"]["arguments"]
            new_parsed_arguments = parse_partial_json(arguments)
            if new_parsed_arguments:
              # Only overwrite what we have if it's not None (which means it failed to parse)
              self.messages[-1]["function_call"][
                "parsed_arguments"] = new_parsed_arguments

        elif self.local:
          pass

      else:
        # We are not in a function call.

        # Check if we just left a function call
        if in_function_call == True:

          if self.local:
            # This is the same as when gpt-4 gives finish_reason as function_call.
            # We have just finished a code block, so now we should run it.
            llama_function_call_finished = True

        # Remember we're not in a function_call
        in_function_call = False

        # If there's no active block,
        if self.active_block == None:

          # Create a message block
          self.active_block = MessageBlock()

      # Update active_block
      self.active_block.update_from_message(self.messages[-1])

      # Check if we're finished
      if chunk["choices"][0]["finish_reason"]:
        if chunk["choices"][0]["finish_reason"] == "function_call":
          # Time to call the function!
          # (Because this is Open Interpreter, we only have one function.)

          if self.debug_mode:
            print("Running function:")
            print(self.messages[-1])
            print("---")

          # Ask for user confirmation to run code
          if self.auto_run == False:

            # End the active block so you can run input() below it
            # Save language and code so we can create a new block in a moment
            self.active_block.end()
            language = self.active_block.language
            code = self.active_block.code

            # Prompt user
            response = input("  Would you like to run this code? (y/n)\n\n  ")
            print("")  # <- Aesthetic choice

            if response.strip().lower() == "y":
              # Create a new, identical block where the code will actually be run
              self.active_block = CodeBlock()
              self.active_block.language = language
              self.active_block.code = code

            else:
              # User declined to run code.
              self.active_block.end()
              self.messages.append({
                "role": "function",
                "name": "run_code",
                "content": "User decided not to run this code."
              })
              return

          # If we couldn't parse its arguments, we need to try again.
          if "parsed_arguments" not in self.messages[-1]["function_call"]:
            self.messages.append({
              "role": "function",
              "name": "run_code",
              "content": """Your function call could not be parsed. Please use ONLY the `run_code` function, which takes two parameters: `code` and `language`. Your response should be formatted as a JSON."""
            })

            self.respond()
            return

          # Create or retrieve a Code Interpreter for this language
          language = self.messages[-1]["function_call"]["parsed_arguments"]["language"]
          if language not in self.code_interpreters:
            self.code_interpreters[language] = CodeInterpreter(language, self.debug_mode)
          code_interpreter = self.code_interpreters[language]

          # Let this Code Interpreter control the active_block
          code_interpreter.active_block = self.active_block
          code_interpreter.run()

          # End the active_block
          self.active_block.end()

          # Append the output to messages
          # Explicitly tell it if there was no output (sometimes "" = hallucinates output)
          self.messages.append({
            "role": "function",
            "name": "run_code",
            "content": self.active_block.output if self.active_block.output else "No output"
          })

          # Go around again
          self.respond()

        if chunk["choices"][0]["finish_reason"] != "function_call":
          # Done!
          self.active_block.end()
          return
