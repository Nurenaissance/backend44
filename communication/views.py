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
from .sentiment_pipeline import analyze_sentiment

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
            group_messages_into_conversations()  # Call the function to group messages
            return Response({"message": "Messages grouped into conversations successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class SentimentAnalysisView(APIView):
    @method_decorator(csrf_exempt, name='dispatch')
    def post(self, request):
        try:
            # Fetch all conversations
            conversations = Conversation.objects.all()
            results = []

            for conversation in conversations:
                result = self.analyze_and_save(conversation)
                if result:
                    results.append(result)

            return Response(results, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def analyze_and_save(self, conversation):
        # Check if sentiment analysis already exists for this conversation
        if SentimentAnalysis.objects.filter(conversation_id=conversation.id).exists():
            # Skip this conversation if sentiment analysis already exists
            return None

        user = conversation.user
        contact = conversation.contact_id
        messages = conversation.messages

        if not user:
            return {'conversation_id': conversation.conversation_id, 'error': 'No user associated with this conversation'}

        if not CustomUser.objects.filter(id=user.id).exists():
            return {'conversation_id': conversation.conversation_id, 'error': f'CustomUser not found for ID: {user.id}'}

        sentiment_scores = analyze_sentiment(messages)

        sentiment_analysis = SentimentAnalysis(
            user=user,
            conversation_id=conversation.id,
            joy_score=sentiment_scores.get('joy', 0),
            sadness_score=sentiment_scores.get('sadness', 0),
            anger_score=sentiment_scores.get('anger', 0),
            trust_score=sentiment_scores.get('love', 0),
            timestamp=timezone.now(),
            contact_id=contact
        )
        sentiment_analysis.save()

        return {'conversation_id': conversation.conversation_id, 'status': 'Processed successfully'}
    
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
