from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('signature/', views.signature_view, name='signature'),
    path('save-signature/', views.save_signature_view, name='save_signature'),
]
