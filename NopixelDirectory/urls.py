from django.contrib import admin
from django.urls import path
from Directory import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.main_page, name="main_page"),
    path('search/', views.search, name = 'search'),
    path('group/<slug:gang_name>/', views.gang_detail, name = 'gang_detail')
]
