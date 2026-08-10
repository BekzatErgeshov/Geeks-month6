from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.testapp.views import RegisterView, CustomTokenObtainPairView, LogoutView, ProfileView

urlpatterns = [
    path('users/register/', RegisterView.as_view(), name='users-register'),
    path('users/login/', CustomTokenObtainPairView.as_view(), name='users-login'),
    path('users/token/refresh/', TokenRefreshView.as_view(), name='users-refresh'),
    path('users/logout/', LogoutView.as_view(), name='users-logout'),
    path('users/profile/', ProfileView.as_view(), name='users-profile'),
]
