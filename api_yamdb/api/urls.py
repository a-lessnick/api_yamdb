from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AuthViewSet #UsersViewSet

router_v1 = DefaultRouter()
# router_v1.register('users', UsersViewSet, basename='users')
router_v1.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
]