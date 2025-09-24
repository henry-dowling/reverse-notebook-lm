from openai import OpenAI
import os
import requests


def write_essay(chat_id: str) -> str:
    transcript: str = get_chat_transcript_from_hume_id(chat_id)

    if not transcript:
        print("No transcript found for chat session.")
        return ""

    openai_client = OpenAI()

    try:
        response = openai_client.responses.create(
            model="gpt-5",
            input=f"""You are a thoughtful essayist with a gift for deep analysis and reflection.
            Please write a compelling, insightful essay about this conversation transcript, analyzing themes,
            emotional undertones, interesting moments, and what the conversation reveals about human
            communication and connection. Write in an engaging, literary style that goes beyond
            surface-level summary to offer genuine insight.

            Conversation transcript:
            {transcript}

            Write the essay in a reflective, literary style that offers deep insights about the conversation."""
        )

        essay = response.output_text
        print("essay is")
        print("="*60)
        print(essay)
        print("="*60 + "\n")

        return essay

    except Exception as e:
        print(f"Error generating essay: {e}")
        return ""

def get_chat_transcript_from_hume_id(chat_id: str) -> str:
    if not chat_id:
        print("DEBUG No chat id!")
        return ""

    result = []
    hume_api_key = os.getenv("HUME_API_KEY")

    try:
        response = requests.get(
            url=f"https://api.hume.ai/v0/evi/chats/{chat_id}",
            headers={
                "X-Hume-Api-Key": hume_api_key,
                "Accept": "application/json; charset=utf-8"
            }
        )

        if response.status_code != 200:
            print(f"Failed to get transcript: {response.status_code}")
            return ""

        data = response.json()
        if 'events_page' not in data:
            print("No events_page in response")
            return ""

        for i, event in enumerate(data['events_page'][1:]):
            print(f"event {i}")
            if 'message_text' in event and event['message_text']:
                print("message text is", event['message_text'])
                result.append(event['message_text'])

        # Join all messages into a single transcript string
        transcript = "\n".join(result)
        print(f"Generated transcript with {len(result)} messages")
        return transcript

    except Exception as e:
        print(f"Error getting transcript: {e}")
        return ""

if __name__ == "__main__":
    write_essay("bc646686-4a30-48f4-be69-3364d927791a")