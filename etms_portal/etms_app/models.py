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


