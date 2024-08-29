from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AuthViewSet, ReviewViewSet, CommentViewSet  # UsersViewSet

router_v1 = DefaultRouter()
# router_v1.register('users', UsersViewSet, basename='users')
router_v1.register(r'auth', AuthViewSet, basename='auth')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router_v1.register(
    r'reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)


urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
