from openai import OpenAI
import os
import requests


def write_essay(chat_id: str) -> str:

    transcript: str = get_chat_transcript_from_hume_id(chat_id)

    openai_client = OpenAI()

    response = openai_client.responses.create(
        model="gpt-5",
        input="Write a one-sentence bedtime story about a unicorn."
    )

    print(response.output_text)

def get_chat_transcript_from_hume_id(chat_id: str) -> str:
    result = []

    hume_api_key = os.getenv("HUME_API_KEY")

    response = requests.get(
        url = f"https://api.hume.ai/v0/evi/chats/{chat_id}",
        headers = {
            "X-Hume-Api-Key": hume_api_key, 
            "Accept": "application/json; charset=utf-8"}
        )
    
    for i, event in enumerate(response.json()['events_page'][1:]):
        print(f"event {i}")
        print("message text is", event['message_text'])
        message = event['message_text']
        if message != None:
            result.append(message)
    
    print("full transcript is", result)

if __name__ == "__main__":
    get_chat_transcript_from_hume_id("bc646686-4a30-48f4-be69-3364d927791a")