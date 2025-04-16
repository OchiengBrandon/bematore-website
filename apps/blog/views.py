# apps/blog/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormMixin
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse, HttpResponseRedirect

from .models import Post, Category, Tag, Comment, Subscription, PostView
from .forms import (PostForm, CommentForm, CategoryForm, TagForm, 
                   SubscriptionForm, PostSearchForm)


class StaffRequiredMixin(UserPassesTestMixin):
    """Verify that the current user is staff"""
    
    def test_func(self):
        return self.request.user.is_staff

class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    paginate_by = 10
    template_name = 'blog/post_list.html'
    
    def get_queryset(self):
        queryset = Post.objects.published()
        
        # Apply search filters if present
        form = PostSearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get('query')
            category = form.cleaned_data.get('category')
            tag = form.cleaned_data.get('tag')
            date_from = form.cleaned_data.get('date_from')
            date_to = form.cleaned_data.get('date_to')
            
            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query) | 
                    Q(content__icontains=query) |
                    Q(excerpt__icontains=query)
                )
            
            if category:
                queryset = queryset.filter(category=category)
                
            if tag:
                queryset = queryset.filter(tags=tag)
                
            if date_from:
                queryset = queryset.filter(published_at__gte=date_from)
                
            if date_to:
                queryset = queryset.filter(published_at__lte=date_to)
                
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = PostSearchForm(self.request.GET or None)
        context['featured_posts'] = Post.objects.published().filter(
            featured__in=['featured', 'hero']
        ).order_by('-featured', '-published_at')[:5]
        context['categories'] = Category.objects.annotate(
            posts_count=Count('post')
        ).filter(is_active=True, posts_count__gt=0)  # Use posts_count for consistency
        context['recent_posts'] = Post.objects.published().order_by('-published_at')[:5]
        return context


class CategoryPostListView(PostListView):
    template_name = 'blog/category_posts.html'
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, 
                                         slug=self.kwargs['slug'], 
                                         is_active=True)
        return super().get_queryset().filter(category=self.category)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class TagPostListView(PostListView):
    template_name = 'blog/tag_posts.html'
    
    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return super().get_queryset().filter(tags=self.tag)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context


class PostDetailView(FormMixin, DetailView):
    model = Post
    context_object_name = 'post'
    form_class = CommentForm
    template_name = 'blog/post_detail.html'
    
    def get_queryset(self):
        if self.request.user.is_staff:
            # Staff can view all posts
            return Post.objects.all()
        # Others can only view published posts
        return Post.objects.published()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(
            is_approved=True, parent=None
        )
        context['related_posts'] = Post.objects.get_related_posts(self.object)
        context['popular_posts'] = Post.objects.get_popular_posts()
        
        # For comment replies
        if self.request.GET.get('reply_to'):
            try:
                parent_id = int(self.request.GET.get('reply_to'))
                context['form'].initial['parent'] = parent_id
                context['replying_to'] = Comment.objects.get(id=parent_id)
            except (ValueError, Comment.DoesNotExist):
                pass
                
        return context
        
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
            
        self.object = self.get_object()
        form = self.get_form()
        
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
            
    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post = self.object
        comment.author = self.request.user
        comment.ip_address = self.request.META.get('REMOTE_ADDR')
        comment.user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        
        # Auto-approve comments from staff
        if self.request.user.is_staff:
            comment.is_approved = True
            
        comment.save()
        messages.success(self.request, 
                        'Your comment has been submitted and is awaiting approval.')
        return super().form_valid(form)
        
    def get_success_url(self):
        return self.object.get_absolute_url()
        
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        
        # Record the view
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None
            
        # Don't count repeated views in the same session
        if not request.session.get(f'viewed_post_{self.object.id}'):
            PostView.objects.create(
                post=self.object,
                user=user,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            request.session[f'viewed_post_{self.object.id}'] = True
            
            # Update post view count
            self.object.increment_views()
            
        return response


class PostCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Post created successfully!')
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Post updated successfully!')
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:post_list')
    template_name = 'blog/post_confirm_delete.html'
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Post deleted successfully!')
        return super().delete(request, *args, **kwargs)


class CategoryCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'blog/category_form.html'


class CategoryUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'blog/category_form.html'


class CategoryDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('blog:category_list')
    template_name = 'blog/category_confirm_delete.html'


class CategoryListView(ListView):
    model = Category
    context_object_name = 'categories'
    template_name = 'blog/category_list.html'
    
    def get_queryset(self):
        return Category.objects.annotate(post_count=Count('post'))


class TagCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Tag
    form_class = TagForm
    template_name = 'blog/tag_form.html'


class TagUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Tag
    form_class = TagForm
    template_name = 'blog/tag_form.html'


class TagDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Tag
    success_url = reverse_lazy('blog:tag_list')
    template_name = 'blog/tag_confirm_delete.html'


class TagListView(ListView):
    model = Tag
    context_object_name = 'tags'
    template_name = 'blog/tag_list.html'
    
    def get_queryset(self):
        return Tag.objects.annotate(post_count=Count('post'))


@login_required
def approve_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to approve comments.')
        return redirect('blog:post_detail', slug=comment.post.slug)
        
    comment.is_approved = True
    comment.save()
    messages.success(request, 'Comment approved successfully!')
    return redirect('blog:post_detail', slug=comment.post.slug)


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Allow staff or the comment author to delete
    if not (request.user.is_staff or request.user == comment.author):
        messages.error(request, 'You do not have permission to delete this comment.')
        return redirect('blog:post_detail', slug=comment.post.slug)
        
    comment.delete()
    messages.success(request, 'Comment deleted successfully!')
    return redirect('blog:post_detail', slug=comment.post.slug)


def subscribe(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            # Check if already subscribed
            email = form.cleaned_data['email']
            if Subscription.objects.filter(email=email).exists():
                messages.info(request, 'You are already subscribed to our blog updates.')
            else:
                form.save()
                messages.success(request, 
                                'Thank you for subscribing to our blog updates!')
            
            # Redirect back to referring page or blog home
            next_page = request.POST.get('next', reverse_lazy('blog:post_list'))
            return HttpResponseRedirect(next_page)
    else:
        form = SubscriptionForm()
        
    return render(request, 'blog/subscription_form.html', {'form': form})


class DraftsListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'blog/drafts_list.html'
    
    def get_queryset(self):
        return Post.objects.filter(status='draft').order_by('-created_at')