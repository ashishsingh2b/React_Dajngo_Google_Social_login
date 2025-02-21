from django.urls import path
from .views import google_auth_url, google_callback

urlpatterns = [
    path("auth/google/authorization", google_auth_url, name="google_auth_url"),
    path("auth/google/callback", google_callback, name="google_callback"),
]
