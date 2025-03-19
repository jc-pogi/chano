from django.db import models
from django.contrib.auth.models import User

class Helmet(models.Model):
    HELMET_TYPES = [
        ('Full Face', 'Full Face'),
        ('Half Face', 'Half Face'),
        ('Modular', 'Modular'),
        ('Off-Road', 'Off-Road'),
        ('Open Face', 'Open Face'),
    ]

    VISOR_TYPES = [
        ('Single Visor', 'Single Visor'),
        ('Double Visor', 'Double Visor'),
    ]

    brand = models.CharField(max_length=100)  # Default brand
    model = models.CharField(max_length=100)  # Default model
    size = models.CharField(max_length=10)  # Default size
    color = models.CharField(max_length=50)  # Default color
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Default price
    quantity = models.IntegerField(default=0)  # Default stock quantity

    # New fields
    helmet_type = models.CharField(max_length=20, choices=HELMET_TYPES, default="Full Face")
    visor_type = models.CharField(max_length=20, choices=VISOR_TYPES, default="Single Visor")

    def __str__(self):
        return f"{self.brand} {self.model} ({self.helmet_type}, {self.visor_type})"


class TransactionLog(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    helmet = models.ForeignKey(Helmet, on_delete=models.CASCADE)
    transaction_date = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=1)  # Default quantity to 1

    def __str__(self):
        return f"{self.user} - {self.helmet}"


class RestockLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    helmet = models.ForeignKey(Helmet, on_delete=models.CASCADE)
    restock_date = models.DateTimeField(auto_now_add=True)
    added_quantity = models.IntegerField(default=0)  # Default restock quantity

    def __str__(self):
        return f"{self.admin} restocked {self.helmet} with {self.added_quantity} units"
