from rest_framework import serializers
from .models import Post, Tag, Comment


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class PostSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    new_tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False,
        help_text="Список новых тегов для создания"
    )

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'tags', 'new_tags', 'author', 'active', 'created_at', 'updated_at']
        read_only_fields = ['author', 'created_at', 'updated_at']

    def create(self, validated_data):
        new_tags = validated_data.pop('new_tags', [])
        post = super().create(validated_data)

        for tag_name in new_tags:
            if not tag_name.strip():
                continue

            tag, _ = Tag.objects.get_or_create(name=tag_name.strip())
            post.tags.add(tag)

        return post


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'post', 'created_at']
        read_only_fields = ['author', 'post', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user

        post = Post.objects.get(pk=self.context['view'].kwargs['post_pk'])

        validated_data['author'] = user
        validated_data['post'] = post

        return Comment.objects.create(**validated_data)

