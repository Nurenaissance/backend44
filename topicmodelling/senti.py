import os
from openai import OpenAI
from interaction.models import Conversation
from communication.models import SentimentAnalysis
from django.db import models

# Set up your OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def get_gradient(score):
    """Map a score to a gradient of emotion intensity."""
    if score <= 3:
        return "Low"
    elif 4 <= score <= 6:
        return "Moderate"
    elif score >= 7:
        return "High"
    return "Unknown"

def analyze_sentiment(text):
    """Analyze sentiment of the given text using OpenAI GPT."""
    try:
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
        "{text}"

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
            return {"error": "No sentiment detected."}

        # Convert the response string into a dictionary
        sentiment_scores = eval(raw_response_content)  # Convert string to dictionary

        return sentiment_scores

    except Exception as e:
        print(f"Error in analyze_sentiment: {str(e)}")
        return None

# Analyze sentiment for all conversations and store in SentimentAnalysis model
def analyze_conversations():
    conversations = Conversation.objects.all()  # Fetch all conversation records
    for conversation in conversations:
        text = conversation.message  # Assuming the conversation model has a 'message' field
        print(f"Analyzing sentiment for conversation ID: {conversation.id}")
        sentiment_scores = analyze_sentiment(text)

        if sentiment_scores and "error" not in sentiment_scores:
            # Extract scores
            joy_score = sentiment_scores["happiness"]
            sadness_score = sentiment_scores["sadness"]
            anger_score = sentiment_scores["anger"]
            trust_score = sentiment_scores["trust"]
            dominant_emotion = sentiment_scores["dominant_emotion"]

            # Store the sentiment scores in the SentimentAnalysis model
            sentiment_analysis = SentimentAnalysis(
                user=conversation.user,  # Assuming conversation has a user field
                message_id=conversation.id,
                joy_score=joy_score,
                sadness_score=sadness_score,
                anger_score=anger_score,
                trust_score=trust_score,
                dominant_emotion=dominant_emotion,  # Store the dominant emotion
                contact_id=conversation.contact_id  # Assuming conversation has a contact_id field
            )
            sentiment_analysis.save()  # Save to the database
            print(f"Sentiment data saved for conversation ID: {conversation.id}")
        else:
            print(f"Skipping conversation ID: {conversation.id}, no sentiment detected.")

# Call the function to analyze all conversations and store the results
analyze_conversations()