from rest_framework import serializers

from api.models import Article


class FullTextSearchSerializer(serializers.ModelSerializer):

    score = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['title', 'body', 'score']

    def get_score(self, obj):
        return obj.score


class ArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = ['title', 'body']

