from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from posts.models import Post
from .models import Comment


def paginateComments(request, comments, results):

    page = request.GET.get('page')
    paginator = Paginator(comments, results)

    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        comments = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        comments = paginator.page(page)

    leftIndex = (int(page) - 4)

    if leftIndex < 1:
        leftIndex = 1

    rightIndex = (int(page) + 5)

    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages + 1

    custom_range = range(leftIndex, rightIndex)

    return custom_range, comments


def get_comments(post: Post):
    return Comment.active_comments.filter(post=post)

    
