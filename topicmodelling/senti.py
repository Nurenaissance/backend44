import os
from openai import OpenAI

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
        - Fear
        - Surprise

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
            "fear": score,
            "surprise": score,
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

        # Add gradient mappings for each emotion
        for emotion, score in sentiment_scores.items():
            if isinstance(score, (int, float)):  # Ensure it's a number before applying the gradient
                sentiment_scores[emotion] = {
                    "score": score,
                    "gradient": get_gradient(score)
                }

        return sentiment_scores

    except Exception as e:
        print(f"Error in analyze_sentiment: {str(e)}")
        return None

# Example usage
text = "I'm feeling great today! The sun is shining and everything seems perfect."
sentiment_scores = analyze_sentiment(text)
print("Sentiment Scores:", sentiment_scores)
