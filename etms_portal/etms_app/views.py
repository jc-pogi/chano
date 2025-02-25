from django.shortcuts import render
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render,redirect


# Create your views here.
def dashboard(request):
    return render(request, "dashboard.html", context={"current_tab": "dashboard"})

def products(request):
    return render(request, "products.html", context={"current_tab": "products"})
def sm(request):
    return render(request, "sm.html", context={"current_tab": "sm"})


def transactions(request):
    return render(request, "transactions.html", context={"current_tab": "transactions"})
def revenue(request):
    return render(request, "revenue.html", context={"current_tab": "revenue"})
def accounts(request):
    return render(request, "accounts.html", context={"current_tab": "accounts"})

def login_view(request):
    if request.method == "POST":
        employee_name = request.POST.get("employee_name", "")
        return redirect("dashboard")
    
    return render(request, "login.html")  # Redirect back if not POST

