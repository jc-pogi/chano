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
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(settings.BASE_DIR, "etms_app", "static", "data.json")
LOGS_FILE = os.path.join(settings.BASE_DIR, "etms_app", "static", "logs.json")

print("📂 JSON Data File Path:", DATA_FILE)  # Debugging log
print("📂 Logs File Path:", LOGS_FILE)  # Debugging log

def create_log_entry(log_type, details):
    """
    Create a log entry and save it to logs.json
    """
    try:
        # Ensure logs file exists
        if not os.path.exists(LOGS_FILE):
            with open(LOGS_FILE, "w") as file:
                json.dump([], file)

        # Read existing logs
        with open(LOGS_FILE, "r") as file:
            logs = json.load(file)

        # Create new log entry
        log_entry = {
            "id": len(logs) + 1,
            "timestamp": datetime.now().isoformat(),
            "type": log_type,
            "details": details
        }

        # Add new log
        logs.append(log_entry)

        # Write back to logs file
        with open(LOGS_FILE, "w") as file:
            json.dump(logs, file, indent=4)

    except Exception as e:
        print(f"Error creating log entry: {e}")

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
                    json.dump({"helmets": [], "logs": []}, file)

            with open(DATA_FILE, "r") as file:
                data = json.load(file)

            # Ensure data has "helmets" and "logs" lists
            if "helmets" not in data:
                data["helmets"] = []
            if "logs" not in data:
                data["logs"] = []

            # Process each new item
            for new_item in new_items:
                # Try to find matching existing product
                matching_product = next((
                    helmet for helmet in data["helmets"]
                    if (helmet["brand"] == new_item["brand"] and
                        helmet["model"] == new_item["model"] and
                        helmet["size"] == new_item["size"] and
                        helmet["color"] == new_item["color"] and
                        helmet["helmet_type"] == new_item["helmet_type"] and
                        helmet["visor_type"] == new_item["visor_type"])
                ), None)

                if matching_product:
                    # Update quantity of existing product
                    old_quantity = matching_product["quantity"]
                    matching_product["quantity"] += new_item["quantity"]
                else:
                    # Add new product if no match found
                    data["helmets"].append(new_item)

                # Create log entry for restock
                log_entry = {
                    "type": "Restock",
                    "brand": new_item["brand"],
                    "model": new_item["model"],
                    "color": new_item["color"],
                    "helmet_type": new_item["helmet_type"],
                    "visor_type": new_item["visor_type"],
                    "quantity": new_item["quantity"],
                    "price": new_item.get("price", "N/A"),
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
                data["logs"].append(log_entry)

            # Save updated data
            with open(DATA_FILE, "w") as file:
                json.dump(data, file, indent=4)

            print("✅ Products Restocked Successfully!")
            return JsonResponse({
                "message": "Products restocked successfully!"
            })

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

            # Update helmet stock and create logs
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
                            
                            # Create log entry for transaction
                            log_entry = {
                                "type": "Transaction",
                                "brand": transaction_item["brand"],
                                "model": transaction_item["model"],
                                "color": transaction_item["color"],
                                "helmet_type": transaction_item["helmet_type"],
                                "visor_type": transaction_item["visor_type"],
                                "quantity": transaction_item["quantity"],
                                "price": transaction_item.get("price", "N/A"),
                                "date": datetime.now().strftime("%Y-%m-%d")
                            }
                            data["logs"].append(log_entry)
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

def update_product(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            with open("data.json", "r+") as file:
                db = json.load(file)
                for product in db["helmets"]:
                    if (product["brand"] == data["brand"] and product["model"] == data["model"]
                            and product["size"] == data["size"] and product["color"] == data["color"]):
                        product["helmet_type"] = data["helmet_type"]
                        product["visor_type"] = data["visor_type"]
                        product["price"] = data["price"]
                        break
                
                file.seek(0)
                json.dump(db, file, indent=4)
                file.truncate()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

# New view to retrieve logs
def get_logs(request):
    try:
        # First, check if logs exist in DATA_FILE (previous implementation)
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as file:
                data = json.load(file)
                logs = data.get("logs", [])
        
        # Then, check if logs exist in LOGS_FILE (new implementation)
        elif os.path.exists(LOGS_FILE):
            with open(LOGS_FILE, "r") as file:
                logs = json.load(file)
        
        else:
            return JsonResponse({"logs": []})
        
        # Sort logs by date in descending order (most recent first)
        logs = sorted(logs, key=lambda x: x.get('date', ''), reverse=True)
        
        return JsonResponse({"logs": logs})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)