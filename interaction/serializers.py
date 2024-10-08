from rest_framework import serializers
from .models import Interaction,Calls, Meetings, Conversation,Email, Group

class InteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = "__all__"

class callsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calls
        fields = "__all__"


class meetingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meetings
        fields = "__all__"

class WhatsappCSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = "__all__"

class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = "__all__"

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'members', 'date_created', 'tenant']

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = '__all__'