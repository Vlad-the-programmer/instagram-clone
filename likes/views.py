import logging
from django.shortcuts import redirect
# Auth
from django.contrib.auth import get_user_model
# Generic class-based views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import edit
from rest_framework.reverse import reverse_lazy

from posts.mixins import GetPostObjectMixin
from .mixins import GetSuccessUrlMixin, GetLikeOrDislikeMixin
from .models import Like, Dislike
from posts.models import Post
from common import mixins as common_mixins
from .utils import get_user_like_and_delete, get_user_dislike_and_delete


logger = logging.getLogger(__name__)

Profile = get_user_model()


class LikeCreateView(LoginRequiredMixin,
                     GetLikeOrDislikeMixin,
                     common_mixins.HandleNotFoundObjectMixin,
                     common_mixins.InvalidFormMixin,
                     GetSuccessUrlMixin,
                     edit.CreateView):
    model = Like
    slug_url_kwarg = 'post_slug'
    context_object_name = 'like'
    template_name = 'posts/post-detail.html'

    
    def post(self, request, *args, **kwargs):
        self.request = request
        
        like, created, post = self.get_object()
        print("Created", created)
        
        if created:
            print("Create like post: ", like.post.title)
            get_user_dislike_and_delete(request.user, post)
            like.post = post
            like.author = request.user
            like.save()
            logger.info(f"Like created by {like.author.username} \
                                for post {like.post.title}")
        return redirect(self.get_success_url())
        
    def form_valid(self, form):
        like, created, _ = self.get_object()
        if created:
            logger.info(f"Like created by {like.author.username} \
                                        for post {like.post.title}")
        return self.get_success_url()


class DislikeCreateView(LoginRequiredMixin,
                        GetLikeOrDislikeMixin,
                        common_mixins.HandleNotFoundObjectMixin,
                        common_mixins.InvalidFormMixin,
                        GetSuccessUrlMixin,
                        edit.DeleteView):
    model = Dislike
    slug_url_kwarg = 'post_slug'
    context_object_name = 'dislike'
    template_name = 'posts/post-detail.html'

    def post(self, request, *args, **kwargs):
        self.request = request
        dislike, created, post = self.get_object()
        logger.info("Created", created)
        
        if created:
            logger.info("Create dislike post: ", dislike.post.title)
            get_user_like_and_delete(request.user, post)
            dislike.post = post
            dislike.author = request.user
            dislike.save()
            logger.info(f"Dislike created by {dislike.author.username} \
                                for post {dislike.post.title}")
            return redirect(self.get_success_url())
        return redirect(self.get_success_url())
        
    
    def form_valid(self, form):
        dislike, created, _ = self.get_object()
        if created:
            logger.info(f"Dislike created by {dislike.author.username} \
                                        for post {dislike.post.title}")
        return self.get_success_url()
    

    
