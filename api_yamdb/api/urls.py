from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (AuthViewSet, ReviewViewSet, CommentViewSet,
                    GenreViewSet, CategoryViewSet, TitleViewSet,
                    UsersViewSet)

router_v1 = DefaultRouter()
router_v1.register('users', UsersViewSet, basename='users')
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

router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('titles', TitleViewSet, basename='titles')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
