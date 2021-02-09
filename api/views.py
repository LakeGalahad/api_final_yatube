from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Follow, Group, Post
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CommentSerializer, FollowSerializer, GroupSerializer, PostSerializer)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['group', ]

    def perform_create(self, serializer, *args, **kwargs):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def perform_create(self, serializer, *args, **kwargs):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs.get('post_id'))
        return post.comments.all()


class ParentViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    pass


class GroupViewSet(ParentViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthorOrReadOnly]


class FollowViewSet(ParentViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', ]

    def get_queryset(self):
        return self.request.user.following.all()

    def perform_create(self, serializer, *args, **kwargs):
        serializer.save(user=self.request.user)
