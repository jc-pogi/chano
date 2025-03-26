import json
from django.shortcuts import redirect

def get_user_role(username):
    with open("data.json", "r") as file:
        data = json.load(file)
        for user in data["users"]:
            if user["username"] == username:
                return user["role"]
    return None

class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/login") or request.path.startswith("/logout"):
            return self.get_response(request)

        if not request.user.is_authenticated:
            return redirect("login")

        role = request.session.get("role")

        print(f"🔍 Checking Access: {request.path} | User Role: {role}")
        # Block non-admins from accessing admin-only pages
        if request.path.startswith(("/dashboard/", "/accounts/", "/products/")) and role != "admin":
            return redirect("transactions")
        

        return self.get_response(request)
