import django_filters
from .models import Post

class PostsFilter(django_filters.FilterSet):
    content = django_filters.CharFilter(lookup_expr='icontains')
    
    author__username = django_filters.CharFilter(lookup_expr='icontains')
    author__country = django_filters.CharFilter(lookup_expr='icontains')
    category__title = django_filters.CharFilter(lookup_expr='icontains')
    tags__title = django_filters.CharFilter(lookup_expr='icontains')
    
    
    release_date = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='created_at',
    )
    release_data_year__gt = django_filters.DateTimeFilter(
        field_name='created_at', 
        lookup_expr='created_at__gt',
    )
    release_data__lt = django_filters.DateTimeFilter(
        field_name='created_at', 
        lookup_expr='created_at__lt',
    )
    
    class Meta:
        model = Post
        fields = [
                  'content',
                  'author__username',
                  'author__country',
                  'category__title',
                  'tags__title',
                  'release_date',
                  ]
    
    