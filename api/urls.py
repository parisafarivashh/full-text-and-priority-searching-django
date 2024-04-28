from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import VectorFullTextSearchAPIView, ArticleReadOnlyViewSet

router = DefaultRouter()
router.register("article", ArticleReadOnlyViewSet, basename="articles")

urlpatterns = [
    path('', VectorFullTextSearchAPIView.as_view()),  # use search_qry in query_params
    path('', include(router.urls))  # use search key-word in url
]

