from django.db import models
from simplecrm.models import CustomUser
from contacts.models import Contact

class SentimentAnalysis(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    conversation_id = models.IntegerField()
    joy_score = models.FloatField()
    sadness_score = models.FloatField()
    anger_score = models.FloatField()
    trust_score = models.FloatField()
    dominant_emotion = models.CharField(max_length=50)  
    timestamp = models.DateTimeField(auto_now_add=True)
    contact_id = models.ForeignKey(Contact, on_delete=models.CASCADE)

class BehavioralMetrics(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    interaction_count = models.IntegerField(default=0)
    average_response_time = models.FloatField(default=0.0)
    last_interaction = models.DateTimeField(null=True, blank=True)
    engagement_score = models.FloatField(default=0.0)

class Conversation(models.Model):
    PLATFORM_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('instagram', 'Instagram'),
        ('email', 'Email'),
        ('call','Call'),
        # Add other platforms if necessary
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    conversation_id = models.CharField(max_length=255, unique=True)
    messages = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    contact_id = models.ForeignKey(Contact, on_delete=models.CASCADE)

class Message(models.Model):
    PLATFORM_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('instagram', 'Instagram'),
        ('email', 'Email'),
        ('call','Call'),
        # Add other platforms if necessary
    ]
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    userid=models.CharField(max_length=5000)  
    mapped = models.BooleanField(default=False)  
