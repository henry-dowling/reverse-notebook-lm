from openai import OpenAI

def write_essay(chat_id: str) -> str:

    #get the transcript from hume
    

    client = OpenAI()

    response = client.responses.create(
        model="gpt-5",
        input="Write a one-sentence bedtime story about a unicorn."
    )

    print(response.output_text)


if __name__ == "__main__":
    main()