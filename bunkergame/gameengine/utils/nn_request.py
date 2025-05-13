from openai import OpenAI
from bunkergame.settings import API_KEY

print(API_KEY)

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=API_KEY,
)
def request_to_nn(message:str):
    completion = client.chat.completions.create(
      model="deepseek/deepseek-r1",
      messages=[
        {
          "role": "user",
          "content": f"""
            Напиши концовку игры как эти персонажи будут выживать бункере одиним абзацом на русском
            {message}
            """
        }
      ]
    )
    return completion.choices[0].message.content