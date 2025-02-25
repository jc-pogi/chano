"""
URL configuration for etms_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path("dashboard/", dashboard, name="dashboard"),
    path("products/", products, name="products"),
    path("sm/", sm, name="sm"),
    path("transactions/", transactions, name="transactions"),
    path("revenue/", revenue, name="revenue"),
    path("accounts/", accounts, name="accounts"),
    path("login/", login_view, name="login"),  # Entransactionssure this exists
]
