from django.shortcuts import render
from .models import Helmet
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def dashboard(request):
    return render(request, "dashboard.html", context={"current_tab": "dashboard"})

def products(request):
    helmets = Helmet.objects.all()
    return render(request, "products.html", {"helmets": helmets})

def sm(request):
    helmets = Helmet.objects.all()
    return render(request, "sm.html", {"helmets": helmets})


def transactions(request):
    helmets = Helmet.objects.all()
    return render(request, "transactions.html", {"helmets": helmets})


def restock(request):
    if request.method == "POST":
        try:
            body_unicode = request.body.decode('utf-8')
            print("Received JSON:", body_unicode)  # Debugging

            data = json.loads(body_unicode)
            items = data.get("items", [])

            if not items:
                return JsonResponse({"status": "error", "message": "No items received."})

            # Process each item
            for item in items:
                print("Processing item:", item)  # Debugging

                required_fields = ["brand", "model", "size", "color", "helmet_type", "visor_type", "price", "quantity"]
                for field in required_fields:
                    if field not in item or item[field] is None:
                        return JsonResponse({"status": "error", "message": f"Missing field: {field}"})

                helmet, created = Helmet.objects.get_or_create(
                    brand=item["brand"],
                    model=item["model"],
                    size=item["size"],
                    color=item["color"],
                    helmet_type=item["helmet_type"],
                    visor_type=item["visor_type"],
                    defaults={"price": item["price"], "quantity": item["quantity"]}
                )

                if not created:
                    helmet.quantity += item["quantity"]
                    helmet.save()

            return JsonResponse({"status": "success", "message": "Restock successful!"})

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON data."})

    helmets = Helmet.objects.all()
    return render(request, "restock.html", {"helmets": helmets})



def revenue(request):
    return render(request, "revenue.html", context={"current_tab": "revenue"})

def accounts(request):
    return render(request, "accounts.html", context={"current_tab": "accounts"})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("employee_name")  # Get username from form
        password = request.POST.get("password")  # Get password from form
        
        # Check if username and password match "admin"
        if username == "admin" and password == "admin":
            return render(request, "dashboard.html", context={"current_tab": "dashboard"})
        
        else:
            messages.error(request, "Invalid username or password")  # Show error message
    
    return render(request, "login.html")  # Render login page
