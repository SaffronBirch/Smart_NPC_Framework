import numpy as np
import ollama

embedding = ollama.embeddings(
    model='mxbai-embed-large', 
    prompt='Represent this sentence for searching relevant passages: The sky is blue because of Rayleigh scattering')

print(embedding)