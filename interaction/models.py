from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from tenant.models import Tenant 
from django.utils import timezone

class Interaction(models.Model):
    INTERACTION_TYPES = (
        ('Call', 'Call'),
        ('Email', 'Email'),
        ('Meeting', 'Meeting'),
        ('Note', 'Note'),
    )

    entity_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    entity_id = models.PositiveIntegerField()
    entity = GenericForeignKey('entity_type', 'entity_id')
    
    interaction_type = models.CharField(max_length=50, choices=INTERACTION_TYPES)
    interaction_datetime = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f'{self.interaction_type} with {self.entity}'

from django.conf import settings
from contacts.models import Contact

class Calls(models.Model):
    call_to = models.ForeignKey(Contact, on_delete=models.SET_NULL, related_name='call_to_meetings', blank=True, null=True, verbose_name='Contact Name')
    related_to = models.CharField(max_length=255, blank=True, null=True, verbose_name='Related To')
    call_type = models.CharField(max_length=255, blank=True, null=True, verbose_name='Call Type')
    outgoing_status = models.CharField(max_length=255, blank=True, null=True, verbose_name='Outgoing Status')
    start_time = models.DateTimeField(verbose_name='Start Time', blank=True, null=True)
    call_duration = models.DurationField(verbose_name='Call Duration', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True, verbose_name='Location')
    voice_recording = models.CharField(max_length=255, blank=True, null=True, verbose_name='Voice Recording')
    to_time = models.DateTimeField(verbose_name='To', blank=True, null=True)
    createdBy = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_calls', on_delete=models.CASCADE, blank=True, null=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.title

from django.contrib.auth.models import User

class Meetings(models.Model):
    title = models.CharField(max_length=64, blank=True, null=True, verbose_name='Title')
    location = models.CharField(max_length=255, blank=True, null=True, verbose_name='Location')
    from_time = models.DateTimeField(verbose_name='From')
    to_time = models.DateTimeField(verbose_name='To')
    related_to = models.CharField(max_length=255, blank=True, null=True, verbose_name='Related To')
    contact_name = models.ForeignKey(Contact, related_name='meeting_contacts', blank=True, null=True, verbose_name='Contact Name', on_delete=models.CASCADE )
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='meeting_hosts', blank=True, null=True, verbose_name='Host')
    participants = models.ForeignKey(Contact, related_name='meeting_participants', blank=True, on_delete=models.CASCADE, null=True)
    description = models.TextField(blank=True, null=True, verbose_name='Description')
    account = models.ForeignKey('accounts.Account', related_name='meetings', on_delete=models.CASCADE, blank=True, null=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='meeting_assigned_users',blank=True, null=True)
    createdBy = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='meeting_created_by', on_delete=models.CASCADE,blank=True, null=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.title

class Conversation(models.Model):
    contact_id = models.CharField(max_length=255)
    message_text = models.TextField()
    sender = models.CharField(max_length=50)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    source=models.CharField(max_length=255)
    date_time = models.DateTimeField(auto_now=True)
    business_phone_number_id = models.CharField(max_length = 255, null=True, blank=True)
    mapped = models.BooleanField(default=False) 



    # Add any other fie1
    # lds you may need

    # Assuming you have tenant-specific tables, add a foreign key to connect them
    # tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE) 

    def __str__(self):
        return f"Conversation ID: {self.id}, Contact ID: {self.contact_id}, Sender: {self.sender}"

class Email(models.Model):
    # Define the choices for the operator
    OPERATOR_CHOICES = (
        ('hostinger', 'Hostinger'),
        ('email', 'Email'),
        ('zoho', 'Zoho'),
        ('outlook', 'Outlook'),
        ('other', 'Other'),
    )

    # Define the choices for the email type
    EMAIL_TYPE_CHOICES = (
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        )
    
    is_open = models.BooleanField(default=False)# Field to track whether the email is open or not 
    time_open = models.DateTimeField(null=True, blank=True)
    tracking_id = models.CharField(max_length=255, unique=True)# Unique identifier for tracking the email
    operator = models.CharField(max_length=20, choices=OPERATOR_CHOICES, null=True, blank=True)# Operator choice field    
    time = models.DateTimeField()# Timestamp for the email
    subject = models.CharField(max_length=255)# Subject of the email
    email_type = models.CharField(max_length=5, choices=EMAIL_TYPE_CHOICES, null=True, blank=True)# Email type choice field
    email_id = models.EmailField(max_length=255) #store the email ID
    links = models.JSONField(default=list) 
    email_html = models.TextField(blank=True, null=True)
    
    open_count = models.IntegerField(default=0)  # Track how many times the email was opened
    total_time_spent = models.DurationField(default=timezone.timedelta(0))  # Total time spent on the email
    attachments = models.JSONField(default=list) # Field to store an array of attachments
    last_open_time = models.DateTimeField(null=True,blank=True)

    def update_time_spent(self, current_time):
        """Update the total time spent on the email."""
        if self.time_open:
            # Calculate the time spent in the current session
            time_spent = current_time - self.time_open
            
            # Update the total time spent on the email
            self.total_time_spent += time_spent
            
            # Reset time_open to None to avoid double-counting for future sessions
            self.time_open = None
            
            # Save the updated instance
            self.save()

    def __str__(self):
        return self.subject
    
class Group(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(Contact, related_name='groups')
    date_created = models.DateTimeField(auto_now_add=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"Group ID: {self.id}, Name: {self.name}, Members: {self.members.count()}"

