from django.shortcuts import render
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.
def dashboard(request):
    return render(request, "dashboard.html", context={"current_tab": "dashboard"})

def products(request):
    return render(request, "products.html", context={"current_tab": "products"})

def sm(request):
    return render(request, "sm.html", context={"current_tab": "sm"})

def transactions(request):
    return render(request, "transactions.html", context={"current_tab": "transactions"})

def restock(request):
    return render(request, "restock.html", context={"current_tab": "restock"})

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