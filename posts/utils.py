from .models import Post
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .filters import PostsFilter


def paginate_posts(request, posts, results):

    page = request.GET.get('page')
    paginator = Paginator(posts, results)

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        posts = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        posts = paginator.page(page)

    leftIndex = (int(page) - 4)

    if leftIndex < 1:
        leftIndex = 1

    rightIndex = (int(page) + 5)

    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages + 1

    custom_range = range(leftIndex, rightIndex)

    return custom_range, posts


def search_posts(request, queryset=None):

    search_query = ''
    posts = queryset
    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')

        posts = Post.published.all().distinct().filter(
            Q(title__icontains=search_query) 
        )
        
    return posts, search_query
    

def posts_filter(request, queryset=None):
    filter = None
    posts = None
    if queryset is not None:
        filter = PostsFilter(request.GET, queryset=queryset)
        posts = filter.qs
    return posts, filter