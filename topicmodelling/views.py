import os
import re
import json
import nltk
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from topicmodelling.models import TopicModelling
from communication.models import Conversation
from openai import OpenAI
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError

# Set up your OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Download necessary NLTK data
nltk.download('stopwords')
nltk.download('punkt')
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    """Preprocess the text using NLTK for tokenization and stopword removal."""
    # Remove unwanted characters and punctuation
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = text.lower()  # Convert to lowercase
    # Tokenize and remove stop words
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)

def perform_topic_modeling(preprocessed_text):
    """Use OpenAI to extract distinct topics from WhatsApp messages in chunks."""
    try:
        # Define the chunk size (max 4000 characters)
        chunk_size = 4000
        topics_set = set()  # Using a set to store unique topics

        # Split the text into chunks if it's longer than chunk_size
        text_chunks = [preprocessed_text[i:i + chunk_size] for i in range(0, len(preprocessed_text), chunk_size)]
        
        for chunk in text_chunks:
            # Construct the prompt for each chunk
            topic_prompt = f"""Analyze the following WhatsApp messages and extract distinct topics.

            Here are the messages:
            {chunk}

            Please list the distinct topics as "Topic 1: [topic name]", "Topic 2: [topic name]", and so on. Do not provide any explanations or details, just list the topics in that format.
            If the messages do not contain distinct topics, respond with 'No topics'."""
            
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": topic_prompt}],
                max_tokens=100 
            )

            # Log the raw response for debugging
            raw_response_content = response.choices[0].message.content.strip()
            print(f"Raw Response from OpenAI for chunk: {raw_response_content}")

            # Split response by lines and clean up the topics
            topics_list = raw_response_content.split("\n")  # Split by newlines
            topics = [topic.strip() for topic in topics_list if topic.strip()]  # Clean up and filter empty lines

            # Add topics to the set (to ensure distinct topics)
            topics_set.update(topics)

         # Convert the set back to a sorted list
        distinct_topics = sorted(list(topics_set))
        
        # Step 2: Get categories from distinct topics
        categorization_prompt = f"""Given the following list of distinct topics, please identify the broader categories they belong to.

        Here are the topics:
        {', '.join(distinct_topics)}

        Please provide a list of unique categories without including any specific topics or explanations. Format your response as a simple list, one category per line."""
        
        # Call OpenAI API for categorization
        categorization_response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": categorization_prompt}],
            max_tokens=100
        )

        # Log the raw response for categorization
        categorized_response = categorization_response.choices[0].message.content.strip()
        print("Categorized Topics Response:", categorized_response)

        # Split the response into categories
        categories = [category.strip() for category in categorized_response.split("\n") if category.strip()]
        
        return categories
    except Exception as e:
        print(f"Error in perform_topic_modeling: {str(e)}")
        return None


@csrf_exempt
def topic_modelling_view(request, conversation_id):
    if request.method == 'POST':
        try:
            # Fetch the conversation from the database
            conversation = get_object_or_404(Conversation, conversation_id=conversation_id)

            # Preprocess the conversation text
            conversation_text = conversation.messages
            preprocessed_text = preprocess_text(conversation_text)

            # Perform topic modeling
            topics = perform_topic_modeling(preprocessed_text)
            if topics is None:
                return JsonResponse({'error': 'Failed to fetch topics from OpenAI'}, status=500)

            # Save topics in the TopicModelling model
            topicmodelling_topicmodelling_entry, created = TopicModelling.objects.update_or_create(
                conversation=conversation,
                user=conversation.user,
                contact_id=conversation.contact_id,
                defaults={'topics': topics}
            )

            return JsonResponse({
                'message': 'Topic modeling completed successfully',
                'topics': topics
            })
        
        except IntegrityError as e:
            # Catch and log the IntegrityError, returning an appropriate message
            print(f"IntegrityError: {str(e)}")
            return JsonResponse({'error': f'Integrity error: {str(e)}'}, status=400)

        except Exception as e:
            # Catch other unexpected errors and log them
            print(f"Unexpected error: {str(e)}")
            return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)
