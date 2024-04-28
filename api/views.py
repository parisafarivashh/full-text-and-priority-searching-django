from django.db.models import Q, Case, When
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Article
from .serializers import ArticleSerializer, FullTextSearchSerializer
from django_filters import rest_framework as filters


class FullTextSearchAPIView(APIView):

    def get(self, request, *args, **kwargs):
        search_qry = request.query_params.get("search_qry")
        articles_obj = Article.objects.filter(title__search=search_qry)
        articles = ArticleSerializer(articles_obj, many=True)
        return Response(articles.data, status=200)


class VectorFullTextSearchAPIView(APIView):

    def get(self, request, *args, **kwargs):
        MINIMUM_MATCH_SCORE = 0.015
        search_qry = request.query_params.get("search_qry", None)
        if not search_qry:
            return Response({"message": "Search query is missing"}, status=400)

        """
            pass the model fields in the SearchVector
            against you want to perform search
            I am passing only title field
        """
        vector = SearchVector("title")
        # Encapsulate the search query parameter
        search_qry = SearchQuery(search_qry)

        articles_obj = Article.objects \
            .annotate(score=SearchRank(vector=vector, query=search_qry)) \
            .filter(score__gte=MINIMUM_MATCH_SCORE) \
            .order_by("-score")

        articles = FullTextSearchSerializer(articles_obj, many=True)
        return Response(articles.data, status=200)


class ArticleFilterSet(filters.FilterSet):
    search = filters.CharFilter(method="filter_by_search")

    class Meta:
        model = Article
        fields = ()

    def filter_by_search(self, queryset, name, value):
        """
        title > body
        """
        if not value:
            return queryset

        queryset = queryset.filter(
            Q(title__icontains=value) | Q(body__icontains=value)
        ).annotate(
            search_priority=Case(
                When(Q(title__icontains=value), then=0),
                When(
                    Q(body__icontains=value) & ~Q(title__icontains=value),
                    then=1,
                ),
                default=2,
            ),
        )

        # Ordering the filtered queryset according to their search priority
        return queryset.order_by("search_priority")


class ArticleReadOnlyViewSet(ReadOnlyModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = ArticleFilterSet


