from rest_framework import generics
from .models import SentimentAnalysis, BehavioralMetrics, Conversation, Message
from .insta_msg import group_messages_into_conversations
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone

from simplecrm.models import CustomUser
from .gpt_utils import generate_reply_from_conversation 
#from .sentiment_pipeline import analyze_sentiment
from django.views.decorators.csrf import csrf_exempt

from .serializers import (
    SentimentAnalysisSerializer,
    BehavioralMetricsSerializer,
    ConversationSerializer,
    MessageSerializer,
)

# Sentiment Analysis Views
class SentimentAnalysisListCreateView(generics.ListCreateAPIView):
    queryset = SentimentAnalysis.objects.all()
    serializer_class = SentimentAnalysisSerializer

class SentimentAnalysisDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SentimentAnalysis.objects.all()
    serializer_class = SentimentAnalysisSerializer

# Behavioral Metrics Views
class BehavioralMetricsListCreateView(generics.ListCreateAPIView):
    queryset = BehavioralMetrics.objects.all()
    serializer_class = BehavioralMetricsSerializer

class BehavioralMetricsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BehavioralMetrics.objects.all()
    serializer_class = BehavioralMetricsSerializer

# Conversation Views
class ConversationListCreateView(generics.ListCreateAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

class ConversationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

# Message Views
class MessageListCreateView(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

class GroupMessagesView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        try:
            tenant_id = request.headers.get('X-Tenant-Id')  # Extract tenant ID from headers
            if not tenant_id:
                return Response({"error": "Missing X-Tenant-Id header."}, status=status.HTTP_400_BAD_REQUEST)
            
            group_messages_into_conversations(tenant_id)  # Call the function to group messages
            return Response({"message": "Messages grouped into conversations successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

import os
import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from openai import OpenAI
from .models import Conversation, SentimentAnalysis

from django.http import JsonResponse, HttpResponseBadRequest
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from communication.models import Conversation
from communication.models import SentimentAnalysis
# Define the OpenAI sentiment analysis function
# Set up your OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
def analyze_sentiment(text):
    """Analyze sentiment of the given text using OpenAI GPT."""
    try:
        # Define the chunk size (max 4000 characters)
        chunk_size = 4000
        sentiment_results = []

        # Split the text into chunks if it's longer than chunk_size
        text_chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

        for chunk in text_chunks:
            # Define the prompt for sentiment analysis
            sentiment_prompt = f"""
            Please analyze the following text and provide a sentiment score for each emotion on a scale from 1 to 10. The emotions to score are:
            - Happiness
            - Sadness
            - Anger
            - Trust

            If the text does not contain any significant emotion, return the response as "No sentiment detected."

            Additionally, identify the dominant emotion based on the scores and provide it in a field named "dominant_emotion." Use the highest score to determine this.

            Here is the text:
            "{chunk}"

            Please respond with a JSON object containing the sentiment scores, like this:
            {{
                "happiness": score,
                "sadness": score,
                "anger": score,
                "trust": score,
                "dominant_emotion": "emotion"
            }}
            """

            # Call the OpenAI API for sentiment analysis
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": sentiment_prompt}]
            )

            # Parse the response
            raw_response_content = response.choices[0].message.content.strip()
            print("Raw Response from OpenAI:", raw_response_content)

            # Check for "No sentiment detected" response
            if "No sentiment detected" in raw_response_content:
                continue  # Skip this chunk if no sentiment detected

            # Convert the response string into a dictionary
            sentiment_scores = eval(raw_response_content)  # Convert string to dictionary
            sentiment_results.append(sentiment_scores)

        # Combine results from all chunks (for example, you could average the scores)
        final_sentiment = {}
        for result in sentiment_results:
            for emotion in ['happiness', 'sadness', 'anger', 'trust']:
                if emotion in final_sentiment:
                    final_sentiment[emotion] += result[emotion]
                else:
                    final_sentiment[emotion] = result[emotion]

        # Average the scores
        num_chunks = len(sentiment_results)
        for emotion in final_sentiment:
            final_sentiment[emotion] /= num_chunks

        return final_sentiment

    except Exception as e:
        print(f"Error in analyze_sentiment: {str(e)}")
        return None

# Define the get_gradient function
def get_gradient(score):
    """Map a score to a gradient of emotion intensity."""
    if score <= 3:
        return "Low"
    elif 4 <= score <= 6:
        return "Moderate"
    elif score >= 7:
        return "High"
    return "Unknown"

@api_view(['POST']) 
def analyze_sentiment_for_conversation(request, conversation_id):
    """Perform sentiment analysis for a specific conversation and store the result."""
    try:
        # Fetch the conversation using the provided ID
        conversation = get_object_or_404(Conversation, conversation_id=conversation_id)

        # Get the text from the conversation
        text = conversation.messages  # Assuming 'message' field contains the conversation text
    
        # Perform sentiment analysis
        sentiment_scores = analyze_sentiment(text)
        if not sentiment_scores or "error" in sentiment_scores:
            return JsonResponse({'error': 'No sentiment detected or failed to analyze.'}, status=400)

        # Extract sentiment scores
        joy_score = sentiment_scores.get("happiness", 0)
        sadness_score = sentiment_scores.get("sadness", 0)
        anger_score = sentiment_scores.get("anger", 0)
        trust_score = sentiment_scores.get("trust", 0)
        dominant_emotion = max(sentiment_scores, key=sentiment_scores.get)  # Find dominant emotion based on highest score

        # Map scores to intensity levels
        joy_gradient = get_gradient(joy_score)
        sadness_gradient = get_gradient(sadness_score)
        anger_gradient = get_gradient(anger_score)
        trust_gradient = get_gradient(trust_score)

        # Store the sentiment scores in the SentimentAnalysis model
        SentimentAnalysis.objects.create(
            user=conversation.user,  # Assuming the Conversation model has a 'user' field
            conversation_id=conversation.id,
            joy_score=joy_score,
            sadness_score=sadness_score,
            anger_score=anger_score,
            trust_score=trust_score,
            dominant_emotion=dominant_emotion,
            contact_id=conversation.contact_id  # Assuming 'contact_id' field in Conversation model
        )

        # Return the response including the sentiment scores and their gradients
        return JsonResponse({
            'message': 'Sentiment analysis completed successfully',
            'sentiment': {
                'happiness': {
                    'score': joy_score,
                    'intensity': joy_gradient
                },
                'sadness': {
                    'score': sadness_score,
                    'intensity': sadness_gradient
                },
                'anger': {
                    'score': anger_score,
                    'intensity': anger_gradient
                },
                'trust': {
                    'score': trust_score,
                    'intensity': trust_gradient
                },
                'dominant_emotion': dominant_emotion
            }
        })

    except Exception as e:
        print(f"Error analyzing sentiment for conversation: {str(e)}")
        return JsonResponse({'error': 'An error occurred during sentiment analysis.'}, status=500)
    
class GenerateReplyView(APIView):
    def get(self, request, conversation_id):
        try:
            # Use the correct field 'conversation_id' to filter the conversation
            conversation = Conversation.objects.filter(conversation_id=conversation_id).first()

            # Check if the conversation exists
            if not conversation:
                return Response({"error": "Conversation with the given conversation_id does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            # Call the function to generate a reply based on the message from the conversation
            reply = generate_reply_from_conversation(conversation_id)

            # If the reply is an error message, return a bad request response
            if "error" in reply.lower() or "does not exist" in reply.lower():
                return Response({"error": reply}, status=status.HTTP_400_BAD_REQUEST)

            # Return the generated reply
            return Response({"reply": reply}, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected errors
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
