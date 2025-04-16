from django.shortcuts import redirect, render, get_object_or_404
from .models import Category, Tag, Post, Comment

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'blog/category_list.html', {'categories': categories})

def tag_list(request):
    tags = Tag.objects.all()
    return render(request, 'blog/tag_list.html', {'tags': tags})

def post_list(request):
    posts = Post.objects.filter(status='published').order_by('-published_at')
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.filter(is_approved=True)
    return render(request, 'blog/post_detail.html', {'post': post, 'comments': comments})

def add_comment(request, post_slug):
    post = get_object_or_404(Post, slug=post_slug)
    if request.method == 'POST':
        content = request.POST.get('content')
        author = request.user  # Assuming the user is logged in
        comment = Comment(post=post, author=author, content=content)
        comment.save()
    return redirect(post.get_absolute_url())