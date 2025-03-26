from django.shortcuts import render
from .decorators import admin_required, user_required
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
@admin_required
def dashboard(request):
    user_role = request.session.get("role", "user")  # Default to "user" if missing
    return render(request, "dashboard.html", context={"current_tab": "dashboard", "user_role": user_role})

@user_required
def products(request):
    user_role = request.session.get("role", "user")
    helmets = Helmet.objects.all()
    context = {
        "helmets": helmets,
        "current_tab": "products",
        "user_role": user_role,
    }
    return render(request, "products.html", context)

@user_required
def transactions(request):
    helmets = Helmet.objects.all()
    user_role = request.session.get("role", "user")
    context = {
        "current_tab": "transactions",
        "helmets": helmets,  # Include helmets inside the same context dictionary
        "user_role": user_role,
    }
    return render(request, "transactions.html", context)

@user_required
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
        user_role = request.session.get("role", "user")  # Default to "user" if missing
        return render(request, "restock.html", context={"current_tab": "restock", "user_role":user_role})

    return JsonResponse({"error": "Invalid request"}, status=400)

@user_required
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
        user_role = request.session.get("role", "user")  # Default to "user" if missing
        return render(request, "transaction.html", context={"current_tab": "transction", "user_role":user_role})

    return JsonResponse({"error": "Invalid request"}, status=400)

@user_required
def revenue(request):
    user_role = request.session.get("role", "user")  # Default to "user" if missing
    return render(request, "revenue.html", context={"current_tab": "revenue", "user_role":user_role})

@admin_required
def accounts(request):
    user_role = request.session.get("role", "user")  # Default to "user" if missing
    return render(request, "accounts.html", context={"current_tab": "accounts", "user_role":user_role})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("employee_name", "").strip()  # Match form field name
        password = request.POST.get("password", "").strip()

        print(f"🛠️ Debug: Login Attempt - Username: {username}")

        with open(DATA_FILE, "r") as file:
            data = json.load(file)
            users = data.get("users", [])

        for user in users:
            print(f"Checking user: {user['username']}")  # Debug
            if user["username"] == username:
                print(f"✅ Found username: {username}, Checking password...")
                if user["password"] == password:  # Check password match
                    request.session["username"] = username
                    request.session["role"] = user["role"]

                    print(f"✅ User Logged In - Username: {username}, Role: {user['role']}")
                    return redirect("dashboard" if user["role"] == "admin" else "transactions")

        print("❌ Invalid credentials, returning to login")
        return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")


def get_products(request):
    try:
        if not os.path.exists(DATA_FILE):
            return JsonResponse({"helmets": []}, safe=False)  # Return empty list if file does not exist
        
        with open(DATA_FILE, "r") as file:
            data = json.load(file)

        return JsonResponse(data.get("helmets", []), safe=False)  # ✅ Return only the helmets list
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
import json

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


def get_user_role(username, password):
    """Fetch user role from JSON database, validating username and password."""
    if not os.path.exists(DATA_FILE):
        return None  # No data file means no users

    with open(DATA_FILE, "r") as file:
        data = json.load(file)

    for user in data.get("users", []):  # Ensure "users" exists
        if user["username"] == username and user["password"] == password:
            return user.get("role")  # ✅ Return role if credentials match

    return None  # No match found

def index(request):
    """Render index.html with user role info."""
    if request.user.is_authenticated:
        role = get_user_role(request.user.username)
        return render(request, "index.html", {"user_role": role})
    return render(request, "index.html", {"user_role": None})
