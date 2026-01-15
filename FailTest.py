import gradio as gr
from LLM import API_helper, _content_to_str
from helper import load_world, save_world, load_env, get_ollama_api_key

############################################## Create Chat UI ##############################################
demo = None

def start_chat(main_loop, share=False):
    # added code to support restart
    global demo
    # If demo is already running, close it first
    if demo is not None:
        demo.close()

    region_names = list(world["regions"].keys())

    demo = gr.ChatInterface(
        fn=main_loop,
        chatbot=gr.Chatbot(height=250, placeholder="Type 'Hello Geralt' to begin"),
        textbox=gr.Textbox(placeholder="What do you say next?", container=False, scale=7),
        title="Chat with Geralt of Rivia",
        # description="Ask Yes Man any question",
        #examples=["How are you?", "Where are you?"],
        cache_examples=False,
        additional_inputs=[gr.Dropdown(choices=region_names, value="White Orchard", label="Start Region")],
        theme=gr.themes.Soft(), 
                           )
    demo.launch(share=share)

def test_main_loop(message, history):
    return 'Entered Action: ' + message

############################################## Initial Start ##############################################
#####
# ADD NEW FUNCTION THAT ALLOWS USER TO SELECT STARTING REGION
# PUT THE CODE BELOW UP TO "run_interaction()" INTO THIS NEW FUNCTION
#####


# Load the world/region/character information from the JSON file
world = load_world('/mnt/c/Users/Saffron/Documents/Ontario Tech Class Notes/Thesis/AI_Powered_Game/TheContinent.json')
region = world['regions']['White Orchard']  # Change region to change start point
character = region['MainCharacter']['Geralt of Rivia']

# Give the LLM instructions on how the act and respond when chatting with a user for the first time
system_prompt = """ 
You are an AI chatbot meant to imitate the character "Geralt of Rivia" from the video game "The Witcher 3: Wild Hunt." \
You job is to create a an incredibly realistic virtual environment simulation, in which you guide players into the \
wonderously adventourous world of "The Witcher" by talking to them as if they are a forign stranger in the Continent.

Instructions:
- You must use only 2-4 sentences. 
- Write in first person. For example: "I am Geralt of Rivia". 
- Write in present tense. For example: "I am looking for...". 
- First describe your character and your backstory. Then describe where you are, and what you see around you. 
"""
# Load the world info
world_info = f"""
World: {world}
Region: {region}
Character: {character}
"""
# Generate the starting output when the user first starts the chat
model_messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": world_info + '\nYour Start:'}
    ]

start = API_helper(model_messages)
print(start)

# Save the starting point of the chat in the JSON file - Currently starting in White Orchard
world['start'] = start
save_world(world, '/mnt/c/Users/Saffron/Documents/Ontario Tech Class Notes/Thesis/AI_Powered_Game/YourWorld.json')

############################################## User Interactions ##############################################

# Define what happens when the user starts the chat for thr first time
def run_interaction(message, history, chat_state, region_name):
    if(message == "Hello Geralt"):
        return chat_state['start']

    # Define what happens when AI responds to user interactions
    system_prompt = """
    Your job is to imitate the character "Geralt of Rivia" from the video game "The Witcher 3: Wild Hunt." \

    Instructions:
    - You must use only 1-3 sentences. 
    - Write in first person.  
    """
    # Provide world info
    world_info = f"""
    World: {chat_state['world']}
    Region: {chat_state['region']}
    Character: {chat_state['character']}
    """
    # System and world messages that get fed into model
    messages = [{"role": "system", "content": system_prompt}]
    messages.append({"role": "user", "content": world_info})
    
    if history:
            if isinstance(history[0], dict):
                # already message dicts
                for h in history:
                    messages.append({
                        "role": h.get("role", "user"),
                        "content": _content_to_str(h.get("content", "")),
                    })
            else:
                # tuples: (user, assistant)
                for u, a in history:
                    if u is not None:
                        messages.append({"role": "user", "content": _content_to_str(u)})
                    if a is not None:
                        messages.append({"role": "assistant", "content": _content_to_str(a)})

    messages.append({"role": "user", "content": _content_to_str(message)})

    return API_helper(messages)

# Define the game state based on the world we've created
chat_state = {
    "world": world['description'],
    "region": region['description'],
    "character": character['description'],
    "start": start,
    "initialized": False,
}

def main_loop(message, history, region_name):
     return run_interaction(message, history, chat_state, region_name)

start_chat(main_loop)