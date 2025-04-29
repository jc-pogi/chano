from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    category = models.CharField(max_length=50)  # e.g., Helmet, Accessory
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.brand})"

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

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sales")
    quantity = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale of {self.product.name} - {self.quantity} units"


