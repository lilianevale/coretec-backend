from openai import OpenAI
import os

client = OpenAI()

def chat_with_gpt(user_input):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um gerador de questões baseado em conteúdos educacionais."},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7,
        max_tokens=700
    )

    return response.choices[0].message.content.strip()

