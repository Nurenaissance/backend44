
from .models import Contact
from .serializers import ContactSerializer
# Create your views here.

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

class ContactListCreateAPIView(ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    # permission_classes = (IsAdminUser,)  # Optionally, add permission classes
    
class ContactDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    # permission_classes = (IsAdminUser,)  # Optionally, add permission classes

class ContactByAccountAPIView(ListCreateAPIView):
    serializer_class = ContactSerializer

    def get_queryset(self):
        account_id = self.kwargs.get('account_id')  # Get account ID from URL parameters
        return Contact.objects.filter(account_id=account_id)  # Filter by 
    
class ContactByPhoneAPIView(ListCreateAPIView):
    serializer_class = ContactSerializer

    def get_queryset(self):
        phone = self.kwargs.get('phone')
        return Contact.objects.filter(phone=phone)