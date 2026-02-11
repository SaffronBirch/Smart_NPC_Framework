from LLM import API_helper
from helper import save_world
from pathlib import Path
import json, re
import keyboard

############################################## Read Game Script File #####################################

def load_script_data(filename):

    base_path = Path(__file__).parent
    file_path = base_path/ "scriptData" / filename

    n = 100000; # Number of tokens to reads (model can't read whole script as its too long)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    elif file_path.suffix.lower() == ".txt":
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

############################################## Read Character Data File #####################################

def load_scratch_data(filename):

    base_path = Path(__file__).parent
    file_path = base_path/ "scatchData" / filename

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    elif file_path.suffix.lower() == ".txt":
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

################################################### Prompts #########################################

#Create the System Prompt
def create_system_prompt():
    return f"""
    Your job is to help create an immersive fantasy world based on a video game.

    Instructions:
    - Return ONLY valid JSON (no markdown, no extra text).
    - Only generate plain JSON.
    - Do not include explanations or commentary.
    - Use simple clear language.
    - You must stay below 3-5 sentences for each description.
    """

#Create the World Prompt
def create_world(game_data):
    return f"""
    - Generate a description of the world that is being created based on the content in {game_data}. 

    Return ONLY valid JSON.

    Schema:
    {{
    "name": "World Name", 
    "description": "World Description"
    }}

    """

#Create the Region Prompt
def create_regions(world, game_data):
    return f"""
    - Generate a description for all of the major regions in {world} based on content in {game_data}.
    - For each regions's description, detail all of the different aspects of the region and all 
        of the people who reside there.

    Return ONLY valid JSON.

    Schema:
    {{
    "regions": [
        {{
        "name": "Region Name", 
        "description": "Region Description"
        }}
    ]
    }}
    """

#Create Characters
def create_characters(world, region, game_data):
    return f""" 
    - Generate a description for all the characters that exist in {region} in the world of {world}. 
    - Describe their appearance, profession, and purpose for being in that particualr region.
    - Describe their backstory based on {game_data}.
    - Describe the chartacters 5 most prevelant personality traits.
    - Generate the name of every other character in {game_data} that knows and/or has a relationship with
        the primary character. Additionlly, describe the nature of their relationship.

    Return ONLY valid JSON.
    Schema:
    {{
    "characters": [
        {{
        "name":"Character Name", 
        "description": "Character Description", 
        "backstory": "Character Backstory",
        "personality": [trait1, trait2, trait3, trait4, trait5],
        "relationships": 
            {{
            "name":"Character Name", 
            "relation": "Nature of Relationship"
            }}
        }}
    ]
    }}
  """

############################################## World/Character Configuration ##############################################
class World:
    def __init__(self, name, description):
        self.name = name 
        self.description = description
    
class Region(World):
    def __init__(self, name, description):
        super().__init__(name, description)

class Character:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def get_personality():
        pass

    def get_relationships():
        pass
    

############################################## Content Generation ##############################################

class WorldGenerator:
    
    def __init__(self, data_filename=None):
       #self.game_name = game_name
       self.system_prompt = create_system_prompt()
       self.world = None
       self.game_data = None

       if data_filename == script_filename:
           self.game_data = load_script_data(data_filename)
       elif data_filename == scratch_filename:
           self.game_data = load_scratch_data(data_filename)
      
   
    def generate_world(self):
       print(f"generating world...")
       
       world_messages = [
           {"role": "system", "content": self.system_prompt},
           {"role": "user", "content": create_world(self.game_data)}]
           
       world_output = API_helper(world_messages)
       world_data = json.loads(world_output)

       self.world = {
          "name": world_data["name"].strip(),
          "description": world_data["description"].strip(),
          "regions": {}
       }

       print(f"Created world: {self.world['name']}")
       return self.world
    
   
    def generate_regions(self):
        if self.world is None:
            raise ValueError("World must be generated first. Call generate_world() first.")
        
        print(f"Generating regions for {self.world}...")

        region_messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": create_regions(self.world, self.game_data)}
        ]
        regions_output = API_helper(region_messages)
        region_data = json.loads(regions_output)
        
        for r in region_data['regions']:
            region_name = r["name"].strip()
            region_description = r["description"].strip()

            self.world['regions'][region_name] = {
                "name": region_name,
                "description": region_description,
                "characters": {}
            }
            print(f"created region {region_name}")
        
        return self.world['regions']
    
  
    def generate_characters(self, region_name):
        if region_name not  in self.world['regions']:
            raise ValueError("Regions must be generated first. Call generate_regions() first.")
        
        print(f"Generating characters for {region_name}...")

        region = self.world['regions'][region_name]

        character_messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": create_characters(self.world, region, self.game_data)}
        ]

        character_output = API_helper(character_messages)
        character_data = json.loads(character_output)

        for c in character_data['characters']:
            character_name = c["name"].strip()
            character_description = c["description"].strip()
            character_backstory = c['backstory'].strip()
            
            region["characters"][character_name] = {
                "name": character_name,
                "description": character_description,
                "backstory": character_backstory
            }
            print(f"created character {character_name}")

        return region['characters']

############################################## Save to JSON ##############################################
 
    def save_to_file(self, filename):
        if self.world is None:
            print("No world has been generated.")

        base_path = Path(__file__).parent
        save_path = base_path/filename

        save_world(self.world, save_path)

############################################## User Input and World Generation ##############################################

script_filename = None
scratch_filename = None

print(f'''
      
    \n === Welcome to the Smart NPC Generator === \n
      
      If you are creating a character from scratch: Press 1 \n
      If you are creating a character from an exising script: Press 2 \n
    '''
    )

# Build NPC from existing script
if keyboard.read_key() == '1':
    generator = WorldGenerator(scratch_filename)

# Build NPC from scratch
elif keyboard.read_key() == '2':
    print(f'''
    Great! Let's get started \n
          
          Step 1) Let's start with where your character lives: \n
          World name: \n
          World description: \n

          Step 2) Describe any regions that populate your world:
          Region name: \n
          Region Description: \n

          Step 3) Create a basic NPC profile: \n
          Character name: \n
          Character Description: \n
          Character Backstory: \n

          Step 4) Give your character more details about their place in the world:
          Which region does your character live in? \n
          Personaity traits (max 5): \n
          Relationships: \n
      '''
      )
    
    generator = WorldGenerator(script_filename)

world = generator.generate_world()
regions = generator.generate_regions()

region_name = None

while region_name not in regions:
    region_name = input("\n Please enter the starting region: ") 
    if region_name in regions:
        characters = generator.generate_characters(region_name)
    else:
        print("Make sure the starting region is typed exactly as seen above.")


filename = f"{world['name'].replace(' ', '')}.json"
generator.save_to_file(filename)






        














