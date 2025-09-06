# %%
from openai import OpenAI, AuthenticationError
import pydub
import os
# %%
short = "./samples/short.mp3"
long = "./samples/long.mp3"
audio_file = open(long, "rb")
# %%
api_key = os.environ.get("OPENAI_API_KEY", "")
client = OpenAI(api_key=api_key)
transcription = client.audio.transcriptions.create(
    model="gpt-4o-transcribe",
    file=audio_file,
    chunking_strategy="auto",
    stream=True,
    language="fa",
    response_format="text",
    prompt="You are a farsi language expert. Please transcribe the following audio in farsi, output should be farsi text with appropriate line breaks and grammar as needed."
)
audio_file.close()
result = ""
text = ""
for event in transcription:
    if event.type == 'transcript.text.delta':
        result+= event.delta
    elif event.type == 'transcript.text.done':
        text = event.text
    else:
        print(event.type)
print(result)
print(text)

# %%
def transcribe(fp,api_key=None):
    audio_file = open(fp, "rb")
    api_key = os.environ.get("OPENAI_API_KEY", "")
    client = OpenAI(api_key=api_key)
    transcription = client.audio.transcriptions.create(
        model="gpt-4o-transcribe",
        file=audio_file,
        chunking_strategy="auto",
        stream=True,
        language="fa",
        prompt="You are a farsi language expert. Please transcribe the following audio in farsi, output should be farsi text with appropriate line breaks and grammar as needed."
    )
    audio_file.close()
    transcribed_text = transcription.text
    return transcribed_text
# %%
print(transcribe("./samples/short.mp3"))
# %%
