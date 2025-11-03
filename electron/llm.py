from ollama import chat
from ollama import ChatResponse

# to set path to detect OLLAMA in powershell: $env:Path += ";C:\Users\Windows\AppData\Local\Programs\Ollama"

system_prompt = {
    'role': 'system',
    'content': """You are a friendly virtual buddy.
- Keep responses short (1–3 sentences).
- Sound casual, like chatting with a friend.
- Ask me little follow-up questions sometimes.
- Avoid long explanations unless I ask for details."""
}

# User’s message
user_message = {
    'role': 'user',
    'content': 'Why is the sky blue?'
}

# Send to Ollama
response: ChatResponse = chat(
    model='gemma3',
    messages=[system_prompt, user_message],
    options={
        'temperature': 0.4,   # more concise
        'top_p': 0.8,
        'num_predict': 80     # limit reply length
    }
)

print(response.message.content)