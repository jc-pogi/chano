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
from .views import restock
from . import views

urlpatterns = [
    path("", login_view, name="login"),
    path("dashboard/", dashboard, name="dashboard"),
    path("products/", products, name="products"),
    path("transactions/", transactions, name="transactions"),
    path("restock/", restock, name="restock"),
    path("get-products/", get_products, name="get_products"),
    path("process_transaction/", process_transaction, name="process_transaction"),
    path("revenue/", revenue, name="revenue"),
    path("accounts/", accounts_view, name="accounts"),
    path('delete_account/', delete_account, name='delete_account'),
    path('add_account/', add_account, name='add_account'),
    path('update_account/', update_account, name='update_account'),
    path("login/", login_view, name="login"),  # Ensure this exists
    path("get-logs/", get_logs, name="get_logs"),
    path('api/product-count/', views.get_product_count, name='product_count'),
    path('api/top-selling-brand/', views.get_top_selling_brand, name='top_selling_brand'),
    path('api/total-stocks/', views.get_total_stocks, name='total_stocks'),
    path('api/low-stock/', views.get_low_stock, name='low_stock'),
    path('api/today-sales/', views.get_today_sales, name='today_sales'),
    path('api/top-selling-brand/', views.get_top_selling_brand, name='top_selling_brand'),
    path('api/top-accessory/', views.get_top_accessory, name='top_accessory'),
    path('api/helmets-sold-today/', views.get_helmets_sold_today, name='helmets_sold_today'),
    path('get_logs/', views.get_logs, name='get_logs'),
    path('api/low-stock-alerts/', views.low_stock_alerts, name='low_stock_alerts'),
]


