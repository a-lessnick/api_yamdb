"""Миксины для вьюсетов."""
from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import PageNumberPagination

from .permissions import IsAdminOrReadOnly


class CreateListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Вьюсет класс для создания и удаления."""

    serializer_class = None
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    search_fields = ('name',)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
