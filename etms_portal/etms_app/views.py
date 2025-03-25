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
from django.conf import settings
import os



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(settings.BASE_DIR, "etms_app", "static", "data.json")

print("📂 JSON Data File Path:", DATA_FILE)  # Debugging log

if not os.path.exists(DATA_FILE):
    print("⚠️ Data file does not exist. Creating a new one.")
    with open(DATA_FILE, "w") as file:
        json.dump([], file)

# Create your views here.
def dashboard(request):
    return render(request, "dashboard.html", context={"current_tab": "dashboard"})

def products(request):
    helmets = Helmet.objects.all()
    context = {
        "helmets": helmets,
        "current_tab": "products"
    }
    return render(request, "products.html", context)


def transactions(request):
    helmets = Helmet.objects.all()
    context = {
        "current_tab": "transactions",
        "helmets": helmets,  # Include helmets inside the same context dictionary
    }
    return render(request, "transactions.html", context)


@csrf_exempt
def restock(request):
    if request.method == "POST":
        try:
            raw_body = request.body.decode("utf-8")
            print("🔍 Received JSON (Raw):", raw_body)

            if not raw_body.strip():
                print("🚨 Empty request body received!")
                return JsonResponse({"error": "Empty request body"}, status=400)

            # Attempt to parse JSON
            try:
                body = json.loads(raw_body)
            except json.JSONDecodeError:
                print("🚨 JSON Decode Error!")
                return JsonResponse({"error": "Invalid JSON format"}, status=400)

            new_items = body.get("items", [])
            if not new_items:
                print("🚨 No items provided in request!")
                return JsonResponse({"error": "No items provided"}, status=400)

            # Load existing data
            if not os.path.exists(DATA_FILE):
                print("⚠️ Data file not found. Creating a new one.")
                with open(DATA_FILE, "w") as file:
                    json.dump({"helmets": []}, file)

            with open(DATA_FILE, "r") as file:
                data = json.load(file)

            # Ensure data has a "helmets" list
            if "helmets" not in data:
                data["helmets"] = []

            # Merge new items with existing ones
            for new_item in new_items:
                found = False
                for existing_item in data["helmets"]:
                    if (
                        existing_item["brand"] == new_item["brand"]
                        and existing_item["model"] == new_item["model"]
                        and existing_item["size"] == new_item["size"]
                        and existing_item["color"] == new_item["color"]
                        and existing_item["helmet_type"] == new_item["helmet_type"]
                        and existing_item["visor_type"] == new_item["visor_type"]
                        and existing_item["price"] == new_item["price"]
                    ):
                        # ✅ Update quantity instead of adding duplicate
                        existing_item["quantity"] += new_item["quantity"]
                        found = True
                        break

                if not found:
                    # ✅ Add new item if it doesn't exist
                    data["helmets"].append(new_item)

            # Save updated data
            with open(DATA_FILE, "w") as file:
                json.dump(data, file, indent=4)

            print("✅ Products Restocked Successfully!")
            return JsonResponse({"message": "Products restocked successfully!"})

        except Exception as e:
            print("⚠️ Unexpected Error:", str(e))
            return JsonResponse({"error": str(e)}, status=500)

    elif request.method == "GET":
        return render(request, "restock.html", {"current_tab": "restock"})

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def process_transaction(request):
    if request.method == "POST":
        try:
            # Load existing data
            if not os.path.exists(DATA_FILE):
                return JsonResponse({"success": False, "message": "Data file not found."})

            with open(DATA_FILE, "r") as file:
                data = json.load(file)

            transaction = json.loads(request.body)
            items = transaction["items"]

            # Update helmet stock
            for transaction_item in items:
                for helmet in data["helmets"]:
                    if (
                        helmet["brand"] == transaction_item["brand"]
                        and helmet["model"] == transaction_item["model"]
                        and helmet["size"] == transaction_item["size"]
                        and helmet["color"] == transaction_item["color"]
                        and helmet["helmet_type"] == transaction_item["helmet_type"]
                        and helmet["visor_type"] == transaction_item["visor_type"]
                    ):
                        if helmet["quantity"] >= transaction_item["quantity"]:
                            helmet["quantity"] -= transaction_item["quantity"]
                        else:
                            return JsonResponse(
                                {"success": False, "message": f"Not enough stock for {transaction_item['brand']} {transaction_item['model']}!"}
                            )

            # Save updated stock back to data.json
            with open(DATA_FILE, "w") as file:
                json.dump(data, file, indent=4)

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    elif request.method == "GET":
        return render(request, "restock.html", {"current_tab": "restock"})

    return JsonResponse({"error": "Invalid request"}, status=400)

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

def get_products(request):
    try:
        if not os.path.exists(DATA_FILE):
            return JsonResponse({"helmets": []}, safe=False)  # Return empty list if file does not exist
        
        with open(DATA_FILE, "r") as file:
            data = json.load(file)

        return JsonResponse(data.get("helmets", []), safe=False)  # ✅ Return only the helmets list
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
