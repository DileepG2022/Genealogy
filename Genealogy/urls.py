"""
URL configuration for Genealogy project.

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
from GenealogyApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', views.family_tree_view, name='family_tree_view'),
    # path('person/<int:person_id>/', views.person_detail, name='person_detail'),
    # path('export/csv/', views.export_family_tree_csv, name='export_family_tree_csv'),
    # path('export/json/', views.export_family_tree_json, name='export_family_tree_json'),
    # path('export/pdf/', views.export_family_tree_pdf, name='export_family_tree_pdf'),

    # Authentication Routes
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Dashboard Route
    path('dashboard/', views.dashboard, name='dashboard'),

    # Family Tree Routes
    path('family_tree/', views.family_tree_dynamic_view, name='family_tree'),
    # path('person/<int:person_id>/', views.person_detail, name='person_detail'),
    path('api/person/<int:person_id>/', views.fetch_person_tree, name='fetch_person_tree'),

    # path("family-tree/", views.family_tree_view, name="family_full_tree"),
    # path("get-children/<int:person_id>/", views.get_children_view, name="get_children"),

    # Export Routes
    path('export/csv/', views.export_family_tree_csv, name='export_family_tree_csv'),
    path('export/json/', views.export_family_tree_json, name='export_family_tree_json'),
    path('export/pdf/', views.export_family_tree_pdf, name='export_family_tree_pdf'),

    path('import_csv/', views.import_csv, name='import_csv'),
]
