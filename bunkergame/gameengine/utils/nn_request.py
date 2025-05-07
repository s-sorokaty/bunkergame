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
            Напиши концовку игры бункер для этих персонажей в этом бункере одиним абзацом на русском
            {message}
            """
        }
      ]
    )
    return completion.choices[0].message.content