from google.adk.models.google_llm import Gemini
from google.genai import Client

model1 = Gemini(model="gemini-2.5-flash")
model1.api_client = Client(api_key="KEY1")

model2 = Gemini(model="gemini-2.5-flash")
model2.api_client = Client(api_key="KEY2")

print(model1.api_client._api_client.api_key)
print(model2.api_client._api_client.api_key)
