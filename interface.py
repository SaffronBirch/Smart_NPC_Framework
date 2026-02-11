'''
NOTES
Users can input their own information into each field, or they can upload a text document which will 
automatically populate the fields based on the provided information.

Personality traits are chosen from a drop down menu that filters the traits based on the keyboard inputs
to make finding specific traits easier.

Relationships are defined by populating a selection of radio buttons with previously created NPCs (if any).
If no other NPCs have been created, a button, when clicked, takes the user back to the NPC profile screen where
they can create another NPC. Or they have the option to just describe a relationship with another character in a text box.
If the text box is used instead, then that characters attributes are automatically use to generate a new NPC by the system
and placed in the world.
When an NPC is clicked on, a text box drops down below where the user can enter the nature of their relationship.
'''

import tkinter as tk

root = tk.Tk()

root.mainloop()

