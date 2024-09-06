from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SentimentAnalysis, Conversation
import os
from openai import OpenAI
from topicmodelling.models import TopicModelling


# Function to fetch sentiment data based on conversation_id
def get_sentiment_data(conversation_id):
    # Fetch sentiment data for the specific conversation
    sentiment = SentimentAnalysis.objects.get(conversation_id=conversation_id)
    return {
        "trust": sentiment.trust_score,
        "joy": sentiment.joy_score,
        "sadness": sentiment.sadness_score,
        "anger": sentiment.anger_score
    }

# Function to fetch topic data based on conversation_id
def get_topic_data(conversation_id):
    # Fetch topic data for the specific conversation
    topic_modeling = TopicModelling.objects.get(conversation_id=conversation_id)
    return topic_modeling.topics

# Function to calculate sentiment score
def calculate_sentiment_score(trust, joy, sadness, anger):
    return ((trust + joy) / 2) - ((sadness + anger) / 2)

# Function to prepare GPT prompt based on sentiment score, channel, and topics
def prepare_gpt_prompt(sentiment_score, channel, topics):
    topics_text = ', '.join(topics) if topics else "No specific topics"
    
   # Determine the tone based on the sentiment score
    if sentiment_score < 2.0:  # Assuming sentiment scores range from 0 (very negative) to 5 (very positive)
        tone = "empathetic and understanding"
        additional_notes = "It's important to acknowledge the customer's feelings and show genuine concern."
    elif sentiment_score < 3.0:
        tone = "supportive and reassuring"
        additional_notes = "Aim to provide comfort and assurance to the customer."
    else:
        tone = "positive and encouraging"
        additional_notes = "Focus on maintaining a friendly and optimistic tone."

    return f"""
    Craft a personalized communication message for the following situation:

    - The customer has a sentiment score of {sentiment_score:.2f}.
    - The preferred communication channel is {channel}.
    - Relevant topics from recent conversations include: {topics_text}.

    The message should:
    - Be {tone}.
    - Address the customer in a friendly and approachable manner.
    - Avoid mentioning specific details like sentiment score or communication channel explicitly.
    - Show appreciation for the customer's interaction and express a willingness to assist if needed.

    Additional Notes:
    - {additional_notes}
    """

# Function to generate personalized prompt based on conversation_id
def generate_personalized_prompt(conversation_id, channel):
    # Retrieve sentiment data
    sentiment_data = get_sentiment_data(conversation_id)
    
    # Retrieve topic data
    topics = get_topic_data(conversation_id)
    
    # Calculate sentiment score
    sentiment_score = calculate_sentiment_score(
        sentiment_data['trust'],
        sentiment_data['joy'],
        sentiment_data['sadness'],
        sentiment_data['anger']
    )
    
    # Prepare GPT prompt
    gpt_prompt = prepare_gpt_prompt(sentiment_score, channel, topics)
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    
    return response.choices[0].message.content.strip()

# API View to handle prompt generation requests
class GeneratePromptView(APIView):
    def post(self, request):
        conversation_id = request.data.get('conversation_id')
        channel = request.data.get('channel')
        
        # Check if conversation_id and channel are provided
        if not conversation_id or not channel:
            return Response(
                {"error": "Conversation ID and channel are required fields."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Generate the personalized prompt
            prompt = generate_personalized_prompt(conversation_id, channel)
            return Response({"prompt": prompt}, status=status.HTTP_200_OK)
        except SentimentAnalysis.DoesNotExist:
            return Response(
                {"error": "Sentiment data for the given conversation ID does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )
        except TopicModelling.DoesNotExist:
            return Response(
                {"error": "Topic data for the given conversation ID does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
 