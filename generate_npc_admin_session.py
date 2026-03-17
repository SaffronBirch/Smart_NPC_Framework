import json
import itertools
import os
 
# Linguistic qualifiers for each of the 9 levels
# Level 1 = extremely low, Level 5 = neutral, Level 9 = extremely high
level_qualifiers = {
    1: ("extremely {low}",      None),
    2: ("very {low}",           None),
    3: ("{low}",                None),
    4: ("a bit {low}",          None),
    5: ("neither {low} nor {high}", None),
    6: ("a bit {high}",         None),
    7: ("{high}",               None),
    8: ("very {high}",          None),
    9: ("extremely {high}",     None),
}
 
# Item instruction variants (ev0-ev4)
item_instructions = [
    "Considering the statement",
    "Thinking about the statement",
    "Reflecting on the statement",
    "Evaluating the statement",
    "Regarding the statement",
]

def build_biography():
    pass

def build_trait_phrase():
    pass






