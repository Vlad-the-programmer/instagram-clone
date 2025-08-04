from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages
# Auth
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
# Generic views
from django.views.generic import list, detail, edit

from comments.forms import CommentCreateForm
from comments.utils import paginateComments
from .models import Post, Tags
from likes.models import Like, Dislike
from .forms import UpdateForm, CreateForm
from .utils import searchPosts, postsFilter, paginatePosts
from . import mixins
from common import mixins as common_mixins
from comments import utils as comment_utils
from common import utils as common_utils


class PostsListView(list.ListView):
    queryset = Post.published.all()
    template_name = 'index.html'
    context_object_name = 'posts'
    
    
    def get(self, request, *args, **kwargs):
        self.request = request
        return super().get(request, *args, **kwargs)
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = context['posts']
        _ , context['filter'] = postsFilter(self.request, self.get_queryset())
        
        if (len(posts) < 5):
            custom_range, page_obj = paginatePosts(self.request, posts, 5) 
        else:                         
            custom_range, page_obj = paginatePosts(self.request, posts, 1)
            
        if self.request.GET.get('content'):
            posts, _ = postsFilter(self.request, self.get_queryset())
            _ , page_obj = paginatePosts(self.request, posts, 5)
        
        # Get post by querying posts by a search_query value
        if self.request.GET.get('search_query'):
            posts, search_query = searchPosts(self.request, self.get_queryset())
            _ , page_obj = paginatePosts(self.request, posts, 5)
            context['search_query'] = search_query
            
        context['page_obj'] = page_obj
        context['custom_range'] = custom_range
        context['posts'] = posts 
        
        print(context)
        return context
    
    
@method_decorator(permission_required("post.add", raise_exception=True), name='dispatch')
class CreatePostView(LoginRequiredMixin, 
                     common_mixins.LoginRequiredMixin,
                     edit.CreateView
                    ):
    model = Post
    form_class = CreateForm
    template_name = 'posts/post_create.html'
    
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            common_utils.set_slug(post, Post.published)
            post.save()
            
            cleaned_tags = form.cleaned_data.get('tags')
            for title in cleaned_tags:
                tag = Tags.objects.get(title=title)
                post.tags.add(tag)
            
            messages.success(request, 'Created!')    
            return redirect(reverse('posts:post-detail', kwargs={'slug': post.slug}))
        messages.error(request, form.errors.as_text())
        return redirect(reverse_lazy('posts:post-create'))
    
    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_text())    
        return redirect(reverse_lazy('posts:post-create'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form_class()
        return context
    
      
class PostDetailView(   mixins.GetPostObjectMixin,
                        detail.DetailView
                    ):
        model = Post
        template_name = 'posts/post-detail.html'
        slug_url_kwarg = 'slug'
        
        
        def delete(self, request, *args, **kwargs):
            self.request = request
            
            post = self.get_object()
            
            if post is None:
                messages.error(request, 'Post does not exist!')    
                return redirect(reverse_lazy("posts:posts-list"))
            return super().delete(request, *args, **kwargs)
    
    
        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            post = context['post']
            
            comments = comment_utils.get_comments(post=post)
            custom_range, page_obj = paginateComments(self.request, comments, 5)
            likes = Like.objects.filter(post__slug=post.slug).all()
            dislikes = Dislike.objects.filter(post__slug=post.slug).all()
            
            context['comment_form'] = CommentCreateForm
            context['comments'] = comments
            context['page_obj'] = page_obj
            context['custom_range'] = custom_range
            context['post_likes'] = likes.count()
            context['post_dislikes'] = dislikes.count()
            
            return context
        
 
@method_decorator(permission_required("post.update", raise_exception=True), name='dispatch')       
class PostUpdateView(   LoginRequiredMixin,  
                        mixins.GetPostObjectMixin, 
                        common_mixins.LoginRequiredMixin,
                        edit.UpdateView
                    ):
    template_name = 'posts/post_create.html'
    form_class = UpdateForm
    
    def post(self, request, *args, **kwargs):
        user = request.user
        post = self.get_object()
        
        if post is None:
            messages.error(request, 'Post does not exist!')    
            return redirect(reverse_lazy("posts:posts-list"))
        
        print(request.POST)
        form = self.form_class( 
                               instance=post, 
                               data=request.POST, 
                               files=request.FILES)
            
        if form.is_valid():
            post = form.save(commit=False)
            print(post)
            post.author = user
            # if not post.slug:
            #     post.slug = slugify(post.title) # slug - AutoSlugField
            post.save()
            
            cleaned_tags = form.cleaned_data.get('tags')
            post.tags.clear()
            
            for cleaned_tag in cleaned_tags:
                tag = Tags.objects.get(title=cleaned_tag.title)
                post.tags.add(tag)
                
            messages.success(request, 'Updated!')    
            return redirect(reverse('posts:post-detail', kwargs={'slug': post.slug}))
        
        messages.error(request, 'Invalid data!')    
        return redirect(reverse('posts:post-detail', kwargs={'slug': post.slug}))

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['form'] = self.form_class(instance=post)
        return context
        

@method_decorator(permission_required("post.delete", raise_exception=True), name='dispatch')
class PostDeleteView(LoginRequiredMixin,   
                        mixins.GetPostObjectMixin,
                        common_mixins.LoginRequiredMixin,
                        edit.DeleteView
                    ):
    template_name = 'posts/post_delete.html'
    success_url = reverse_lazy('posts:posts-list')
    
    
    def delete(self, request, *args, **kwargs):
        self.request = request
        return super().delete(request, *args, **kwargs)
        
        
    def form_valid(self, form):
        post = self.get_object()
        if post:
            post.delete()
            messages.success(self.request, 'Post deleted!')
            return redirect(self.success_url)
        else:
            messages.error(self.request, 'Post does not exist!')
            
            context={}
            context['post'] = post
            
            return render(self.request, self.template_name, context)


