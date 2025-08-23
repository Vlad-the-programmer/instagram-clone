from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import PermissionDenied
from django.db import transaction

from posts.models import Post, Tags
from posts.views import PostsListView, CreatePostView, PostDetailView, PostUpdateView, PostDeleteView
from comments.models import Comment

import tempfile
import shutil
from PIL import Image
import os


User = get_user_model()


class TestPostsViews(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User._default_manager.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User._default_manager.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Create a test image
        self.test_image = self.create_test_image()
        
        # Create a tag
        self.tag = Tags.objects.create(title='testtag')
        
        # Create a test post
        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            author=self.user,
            content='This is a test post content',
            status='published'
        )
        self.post.tags.add(self.tag)
        
        # Create a comment
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment'
        )
    
    def tearDown(self):
        # Clean up the test image directory
        if os.path.exists('media/test_images'):
            shutil.rmtree('media/test_images')

    def _login(self, user=None, email=None, password=None) -> Client:
        """Helper method to log in a user for tests."""
        if user:
            email = user.email
            password = 'testpass123'  # Default password used in setup

        # Create a request factory
        factory = RequestFactory()
        request = factory.post(reverse('account_login'), {
            'login': email,
            'password': password,
        })
        request.user = user if user else self.user

        # Manually set up the session
        from django.contrib.sessions.middleware import SessionMiddleware
        from django.contrib.auth.middleware import AuthenticationMiddleware
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        # Add authentication middleware
        auth_middleware = AuthenticationMiddleware(lambda req: None)
        auth_middleware.process_request(request)

        # Use the test client to log in
        self.client.force_login(
            user if user else self.user,
            backend='allauth.account.auth_backends.AuthenticationBackend'
        )

        self.assertEqual(request.user.is_authenticated, True)
        return self.client

    def create_test_image(self):
        # Create a temporary image file
        image = Image.new('RGB', (100, 100), 'white')
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        image.save(tmp_file, 'JPEG')
        tmp_file.seek(0)
        return SimpleUploadedFile(
            name='test_image.jpg',
            content=tmp_file.read(),
            content_type='image/jpeg'
        )
    
    def test_posts_list_view(self):
        """Test that the posts list view returns a 200 status code and uses the correct template."""
        url = reverse('posts:posts-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertIn('posts', response.context)
        self.assertEqual(len(response.context['posts']), 1)  # Should have our test post
    
    def test_posts_list_search(self):
        """Test that search functionality works in the posts list view."""
        url = reverse('posts:posts-list') + '?search_query=Test'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts']), 1)  # Should find our test post
        
        # Test with non-matching search
        url = reverse('posts:posts-list') + '?search_query=nonexistent'
        response = self.client.get(url)
        self.assertEqual(len(response.context['posts']), 0)
    
    def test_create_post_view_requires_login(self):
        """Test that creating a post requires login."""
        url = reverse('posts:post-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Should redirect to login
    
    def test_create_post_view_get(self):
        """Test the GET request to create post view."""
        self._login(self.user)

        url = reverse('posts:post-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/post_create.html')
        self.assertIn('form', response.context)
    
    def test_create_post_view_post(self):
        """Test creating a new post."""
        self._login(self.user)
        url = reverse('posts:post-create')
        
        data = {
            'title': 'New Test Post',
            'content': 'This is a new test post',
            'status': 'published',
            'tags': [self.tag.pk]
        }
        
        with self.test_image as img:
            data['image'] = img
            response = self.client.post(url, data, follow=True)
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(Post.objects.filter(title='New Test Post').exists())
            
            # Verify the post was created with the correct data
            post = Post.objects.get(title='New Test Post')
            self.assertEqual(post.author, self.user)
            self.assertEqual(post.status, 'published')
            self.assertTrue(post.tags.filter(pk=self.tag.pk).exists())
    
    def test_post_detail_view(self):
        """Test viewing a single post."""
        url = reverse('posts:post-detail', kwargs={'slug': self.post.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/post-detail.html')
        self.assertEqual(response.context['post'], self.post)
        self.assertIn('comments', response.context)
        self.assertIn('comment_form', response.context)
    
    def test_update_post_view_get(self):
        """Test the GET request to update post view."""
        self._login(self.user)
        url = reverse('posts:post-update', kwargs={'slug': self.post.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/post_create.html')
        self.assertIn('form', response.context)
    
    def test_update_post_view_post(self):
        """Test updating an existing post."""
        self._login(self.user)
        url = reverse('posts:post-update', kwargs={'slug': self.post.slug})
        
        # Create a new tag for the update
        new_tag = Tags.objects.create(title='updatedtag')
        
        data = {
            'title': 'Updated Test Post',
            'content': 'This is an updated test post',
            'status': 'draft',
            'tags': [new_tag.pk]
        }
        
        with self.test_image as img:
            data['image'] = img
            response = self.client.post(url, data, follow=True)
            
            self.assertEqual(response.status_code, 200)
            
            # Refresh the post from the database
            self.post.refresh_from_db()
            
            # Verify the post was updated with the correct data
            self.assertEqual(self.post.title, 'Updated Test Post')
            self.assertEqual(self.post.status, 'draft')
            self.assertTrue(self.post.tags.filter(pk=new_tag.pk).exists())
    
    def test_delete_post_view(self):
        """Test deleting a post."""
        self._login(self.user)
        url = reverse('posts:post-delete', kwargs={'slug': self.post.slug})
        
        # Test GET request (confirmation page)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/post_delete.html')
        
        # Test POST request (actual deletion)
        post_count = Post.objects.count()
        response = self.client.post(url, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), post_count - 1)
        self.assertRedirects(response, reverse('posts:posts-list'))
    
    def test_post_permissions(self):
        """Test that users can only modify their own posts."""
        # Create a second user
        user2 = User._default_manager.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # Test update permission
        self._login(self.user)
        url = reverse('posts:post-update', kwargs={'slug': self.post.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)  # Should be forbidden
        
        # Test delete permission
        url = reverse('posts:post-delete', kwargs={'slug': self.post.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)  # Should be forbidden
        
        # Admin should have access
        self._login(self.admin_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)  # Admin can access

    def test_pagination(self):
        """Test that pagination works correctly."""
        # Create enough posts to trigger pagination
        for i in range(15):
            Post.objects.create(
                title=f'Test Post {i}',
                slug=f'test-post-{i}',
                author=self.user,
                content=f'Test content {i}',
                status='published'
            )
        
        # First page should have 5 posts (pagination is set to 5 in the view)
        response = self.client.get(reverse('posts:posts-list'))
        self.assertEqual(len(response.context['posts']), 5)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        
        # Second page should have the remaining posts
        response = self.client.get(reverse('posts:posts-list') + '?page=2')
        self.assertEqual(len(response.context['posts']), 11)  # 16 total - 5 on first page

    def test_invalid_post_handling(self):
        """Test handling of non-existent posts."""
        # Test non-existent post detail
        response = self.client.get(reverse('posts:post-detail', kwargs={'slug': 'non-existent'}))
        self.assertEqual(response.status_code, 404)
        
        # Test non-existent post update
        self._login(self.user)
        response = self.client.get(reverse('posts:post-update', kwargs={'slug': 'non-existent'}))
        self.assertEqual(response.status_code, 404)
        
        # Test non-existent post delete
        response = self.client.get(reverse('posts:post-delete', kwargs={'slug': 'non-existent'}))
        self.assertEqual(response.status_code, 404)
