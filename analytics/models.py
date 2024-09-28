from django.db import models
from tenant.models import Tenant

class Customer(models.Model):
    name = models.CharField(max_length=100)

class Transaction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

class CLTV(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    cltv_value = models.DecimalField(max_digits=10, decimal_places=2)

class FAISSIndex(models.Model):
    name = models.CharField(max_length=100)
    index_data = models.BinaryField()
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)

class userData(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    phone = models.BigIntegerField()
    doc_name = models.CharField(max_length=100)
    data = models.JSONField()
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
