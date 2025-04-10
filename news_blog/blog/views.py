from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Post, Tag, Comment
from .serializers import PostSerializer, TagSerializer, CommentSerializer
from .permissions import IsOwnerOrAdmin



class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer

    queryset = Post.objects.all().prefetch_related('tags')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    filterset_fields = {
        'tags__name': ['exact', 'icontains'],
        'tags__id': ['exact'],
    }

    search_fields = ['tags__name', 'title', 'content']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        queryset = self.queryset
        if not self.request.user.is_staff:
            queryset = queryset.filter(active=True)
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        queryset = self.queryset
        post_id = self.kwargs.get('post_pk')
        return queryset.filter(post_id=post_id).order_by('-created_at')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsOwnerOrAdmin()]

    def perform_create(self, serializer):
        post = Post.objects.get(pk=self.kwargs['post_pk'])
        serializer.save(author=self.request.user, post=post)
