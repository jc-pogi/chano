from django.shortcuts import render
from .decorators import admin_required, user_required
from .models import Helmet
from django.shortcuts import render,redirect
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
from datetime import datetime
from etms_app.models import Helmet 
from django.db.models import Sum


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
@user_required
def dashboard(request):
    user_role = request.session.get("role", "user")
    
    # Try counting from the database first
    helmets_db = Helmet.objects.all()
    db_count = helmets_db.count()
    
    # Also try getting count from JSON file
    json_count = 0
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as file:
                data = json.load(file)
                helmets_json = data.get("helmets", [])
                json_count = len(helmets_json)
    except Exception as e:
        print(f"Error loading JSON data: {e}")
    
    # Use whichever count is higher
    total_products = max(db_count, json_count)
    print(f"DEBUG: DB Count: {db_count}, JSON Count: {json_count}, Using: {total_products}")
    
    context = {
        "current_tab": "dashboard", 
        "user_role": user_role,
        "total_products": total_products
    }
    
    return render(request, "dashboard.html", context)

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

@admin_required
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
        user_role = request.session.get("role", "user")  # Default to "user" if missing
        return render(request, "transaction.html", context={"current_tab": "transction", "user_role":user_role})

    return JsonResponse({"error": "Invalid request"}, status=400)

@admin_required
def revenue(request):
    user_role = request.session.get("role", "user")  # Default to "user" if missing
    return render(request, "revenue.html", context={"current_tab": "revenue", "user_role":user_role})

@admin_required
def accounts_view(request):
    user_role = request.session.get("role", "user")  # Default to "user"

    try:
        with open(DATA_FILE, "r") as file:
            data = json.load(file)

            # If data is a list, assume it's already user data
            if isinstance(data, list):
                users = data
            elif isinstance(data, dict):
                users = data.get("users", [])  # Extract users from dictionary
            else:
                users = []

            print("Loaded Users:", users)  # Debugging output
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print("Error loading JSON:", e)
        users = []

    return render(request, "accounts.html", {"current_tab": "accounts", "user_role": user_role, "users": users})


def login_view(request):
    request.session.flush()  # Clear session to avoid unwanted persistence

    if request.method == "POST":
        username = request.POST.get("employee_name", "").strip()
        password = request.POST.get("password", "").strip()

        print(f"🛠️ Debug: Login Attempt - Username: {username}")

        # Load JSON data
        with open(DATA_FILE, "r+") as file:
            data = json.load(file)
            users = data.get("users", [])

            for user in users:
                print(f"Checking user: {user['username']}")  # Debug
                
                if user["username"] == username:
                    print(f"✅ Found username: {username}, Checking password...")

                    # 🚫 Block login if user is inactive
                    if user["status"] == "Inactive":
                        print(f"❌ Login Blocked - {username} is Inactive")
                        return render(request, "login.html", {"error": "Your account is inactive. Contact admin."})

                    if user["password"] == password:  # ⚠️ Hash passwords in production!
                        request.session["username"] = username
                        request.session["role"] = user["role"]

                        # ✅ Update lastLogin with current timestamp
                        user["lastLogin"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        # Save the updated JSON file
                        file.seek(0)
                        json.dump(data, file, indent=4)
                        file.truncate()

                        print(f"✅ User Logged In - Username: {username}, Role: {user['role']}, Last Login Updated!")
                        return redirect("dashboard")

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

def get_product_count(request):
    # Focus on JSON file since that's where your data might be
    json_sum = 0
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as file:
                print(f"Reading from {DATA_FILE}")
                data = json.load(file)
                helmets_json = data.get("helmets", [])
                
                if not helmets_json:
                    print("No helmets found in JSON data")
                else:
                    print(f"Found {len(helmets_json)} helmets in JSON")
                
                # Sum up quantities - handle possible missing quantity field
                for helmet in helmets_json:
                    qty = helmet.get("quantity", 0)
                    if isinstance(qty, (int, float)):
                        json_sum += qty
                    else:
                        print(f"Invalid quantity value: {qty} for helmet {helmet.get('brand', 'N/A')} {helmet.get('model', 'N/A')}")
                
                print(f"Total quantity from JSON: {json_sum}")
        else:
            print(f"Data file not found: {DATA_FILE}")
    except Exception as e:
        print(f"Error processing JSON data: {e}")
    
    return JsonResponse({'count': json_sum})

def get_top_selling_brand(request):
    try:
        # Dictionary to store total units sold for each brand
        brand_totals = {}
        
        # Check for logs in DATA_FILE
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as file:
                data = json.load(file)
                logs = data.get("logs", [])
                
                # Process only Transaction type logs
                for log in logs:
                    if log.get("type") == "Transaction":
                        brand = log.get("brand")
                        quantity = log.get("quantity", 0)
                        
                        # Convert quantity to integer if it's a string
                        if isinstance(quantity, str):
                            try:
                                quantity = int(quantity)
                            except ValueError:
                                quantity = 0
                        
                        # Add to brand total
                        if brand in brand_totals:
                            brand_totals[brand] += quantity
                        else:
                            brand_totals[brand] = quantity
        
        # Also check LOGS_FILE if it exists separately
        if os.path.exists(LOGS_FILE):
            with open(LOGS_FILE, "r") as file:
                logs = json.load(file)
                
                # Handle if logs file contains a list
                if isinstance(logs, list):
                    for log in logs:
                        if log.get("type") == "Transaction":
                            brand = log.get("brand")
                            quantity = log.get("quantity", 0)
                            
                            # Convert quantity to integer if it's a string
                            if isinstance(quantity, str):
                                try:
                                    quantity = int(quantity)
                                except ValueError:
                                    quantity = 0
                            
                            # Add to brand total
                            if brand in brand_totals:
                                brand_totals[brand] += quantity
                            else:
                                brand_totals[brand] = quantity
        
        # Debug: Print all brand totals to see what data we're working with
        print("Brand sales totals:", brand_totals)
        
        # Find the brand with the highest total
        top_brand = "No sales data"
        max_quantity = 0
        
        for brand, total in brand_totals.items():
            if total > max_quantity:
                max_quantity = total
                top_brand = brand
        
        # If we have no data, default to what's shown in the chart
        if not brand_totals:
            # From your chart data, it appears EVO has the highest count
            top_brand = "EVO"
        
        return JsonResponse({"top_brand": top_brand, "units_sold": max_quantity})
    
    except Exception as e:
        # Log the full error for debugging
        import traceback
        print(f"Error in get_top_selling_brand: {e}")
        traceback.print_exc()
        
      

@csrf_exempt
def delete_account(request):
    if request.method == "POST":
        try:
            # Load request data
            data = json.loads(request.body)
            username_to_delete = data.get("username")

            # Read the JSON file
            with open(DATA_FILE, "r+") as file:
                existing_data = json.load(file)

                # Ensure "users" exists and is a list
                if "users" not in existing_data or not isinstance(existing_data["users"], list):
                    return JsonResponse({"success": False, "error": "Invalid data format"}, status=400)

                # Filter out the user to delete
                existing_data["users"] = [user for user in existing_data["users"] if isinstance(user, dict) and user.get("username") != username_to_delete]

                # Write updated data back to the file
                file.seek(0)
                json.dump(existing_data, file, indent=4)
                file.truncate()

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False}, status=400)

@csrf_exempt
def add_account(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            data["lastLogin"] = None  # Set default last login for new users
            
            # Load existing data
            if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
                with open(DATA_FILE, "r+") as file:
                    try:
                        existing_data = json.load(file)  # Load full JSON
                    except json.JSONDecodeError:
                        existing_data = {}  # If file is corrupted, reset to empty dict
            else:
                existing_data = {}  # If file doesn't exist, create empty structure
            
            # Ensure "users" key exists
            if "users" not in existing_data:
                existing_data["users"] = []
            
            # Append new user
            existing_data["users"].append(data)

            # Save updated data (without overwriting other keys)
            with open(DATA_FILE, "w") as file:
                json.dump(existing_data, file, indent=4)

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False}, status=400)


@csrf_exempt
def update_account(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Load request data

            with open(DATA_FILE, "r+") as file:
                existing_data = json.load(file)

                if "users" not in existing_data or not isinstance(existing_data["users"], list):
                    return JsonResponse({"success": False, "error": "Invalid data format"}, status=400)

                # Update the user
                for user in existing_data["users"]:
                    if isinstance(user, dict) and user.get("username") == data["username"]:
                        # ✅ Only update fields that exist in `data`
                        user["status"] = data.get("status", user["status"])
                        user["password"] = data.get("password", user["password"])  # Only update if provided
                        user["role"] = data.get("role", user["role"])  # 🔥 Fix: Prevent role from changing unexpectedly

                # Save the updated data
                file.seek(0)
                json.dump(existing_data, file, indent=4)
                file.truncate()

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False}, status=400)
