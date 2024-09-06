from communication.models import Conversation
from openai import OpenAI
import os
def generate_reply_from_conversation(conversation_id):
    try:
        # Retrieve the conversation object and message
        conversation = Conversation.objects.get(conversation_id=conversation_id)
        message = conversation.messages

        # Prepare the GPT prompt
        gpt_prompt = f"The user sent the following message: '{message}'. Please generate a human-like reply email responding appropriately to this message."

        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Generate a response from GPT
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates natural and engaging communication prompts."},
                {"role": "user", "content": gpt_prompt}
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )

        # Extract the generated reply
        gpt_reply = response.choices[0].message.content

        return gpt_reply

    except Conversation.DoesNotExist:
        return "Conversation with the given ID does not exist."
    except Exception as e:
        return f"An error occurred: {str(e)}"