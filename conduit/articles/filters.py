from django_filters import rest_framework as filters
from conduit.articles.models import Article


class ArticleFilter(filters.FilterSet):
    tag = filters.CharFilter(field_name='tags__name')
    author = filters.CharFilter(field_name='author__email')
    favorited = filters.CharFilter(method='filter_favorited')
    limit = filters.NumberFilter(method="limit_filter")
    offset = filters.NumberFilter(method="offset_filter")

    class Meta:
        model = Article
        fields = ['tag', 'author', 'favorited', 'limit', 'offset']

    def filter_favorited(self, queryset, name, value):
        return queryset.filter(favorites__email=value)

    def limit_filter(self, queryset, name, value):
        return queryset[:value]

    def offset_filter(self, queryset, name, value):
        return queryset[value:]
