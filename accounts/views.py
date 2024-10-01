from .models import Account
from .serializers import AccountSerializer
from rest_framework.permissions import AllowAny
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import AccountSerializer

class AccountListCreateAPIView(ListCreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = (AllowAny,)
   

class AccountDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = (AllowAny,)  # Allowing any user to access this view

    # def get_queryset(self):
    #     # Filter queryset based on user's tenant
    #     user_tenant = self.request.user.tenant
    #     return Account.objects.filter(tenant=user_tenant)

    # def perform_create(self, serializer):
    #     # Set the tenant of the account before saving
    #     serializer.save(tenant=self.request.user.tenant)

