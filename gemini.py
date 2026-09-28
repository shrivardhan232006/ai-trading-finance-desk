
import base64
import time
from google import genai
client = genai.Client()
"""
user_question = "tell me about mit in a story"
time1 = time.time()
interaction = client.interactions.create(
    model="gemini-2.5-flash",
    
    stream= True,
    input= user_question
    
)

for event in interaction:
    if event.event_type == "step.delta":
        if event.delta.type == "text":
            # print(event.delta.text, end="", flush=True)
            with open('output.txt', 'a', encoding = 'utf_8') as f:
                f.write(event.delta.text)

time2 = time.time()
print(time2 - time1)"""

interaction = client.interactions.create(
    model="gemini-2.5-flash-image",
    input="Generate an image of a futuristic city skyline at sunset",
)

with open("generated_image.png", "wb") as f:
    f.write(base64.b64decode(interaction.output_image.data))