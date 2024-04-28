## The basic full-text search in Django

Most simply, we can just use Postgres “__search” lookup and our job will be done!

### When should you use __search lookup?

1) When you want to implement a quick and basic full-text search
2) When you don’t want to search against multiple fields at once
3) When you don’t want to customize the full-text search like Rank etc…


## The more convenient way
Django’s “django.contrib.postgres.search” module offers convenient classes like SearchVector, SearchQuery, and SearchRank for implementing full-text search functionality with more controls.

## SearchVector: 
SearchVector is a PostgreSQL data type that represents a document’s vector, which contains the textual content to be searched. In other words, you can think it converts the column values into vectors.


## SearchQuery: 
SearchQuery represents the search query or phrase that you want to search. It encapsulates or packages the search query into a format that Django can understand and use to perform the full-text search operation.

## SearchRank: 
SearchRank is a PostgreSQL function used to rank search results based on their relevance to the search query, it does the same job in Django.


# Priority-Based Search In Django
Here, I would like to have a priority such that articles matching with title 
will display before those matching with body.
The whole priority would be like this: title > body

-write custom class filtering

```
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

