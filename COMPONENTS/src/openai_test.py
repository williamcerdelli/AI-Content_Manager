import openai

from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

response = openai.Completion.create(
  model="text-davinci-003",
  prompt="write a short story\n",
  temperature=0.5,
  max_tokens=60,
  top_p=0.3,
  frequency_penalty=0.5,
  presence_penalty=0
)
print(response)
