from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Solution, Feature

def solution_list(request):
    # Get filter parameters
    platform_filter = request.GET.get('platform', None)
    search_query = request.GET.get('search', None)
    
    # Start with all active solutions
    solutions = Solution.objects.filter(is_active=True)
    
    # Apply filters if provided
    if platform_filter and platform_filter != 'all':
        solutions = solutions.filter(platform=platform_filter)
    
    if search_query:
        solutions = solutions.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Order by the specified field
    solutions = solutions.order_by('order')
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(solutions, 6)  # Show 6 solutions per page
    
    try:
        solutions_page = paginator.page(page)
    except PageNotAnInteger:
        solutions_page = paginator.page(1)
    except EmptyPage:
        solutions_page = paginator.page(paginator.num_pages)
    
    # Get platform choices for the filter dropdown
    platform_choices = Solution.PLATFORM_CHOICES
    
    context = {
        'solutions': solutions_page,
        'platform_choices': platform_choices,
        'current_platform': platform_filter,
        'search_query': search_query,
    }
    
    return render(request, 'solutions/solution_list.html', context)

def solution_detail(request, slug):
    # Get the solution or 404
    solution = get_object_or_404(Solution, slug=slug, is_active=True)
    
    # Get related solutions (same platform but different)
    related_solutions = Solution.objects.filter(
        platform=solution.platform, 
        is_active=True
    ).exclude(id=solution.id)[:3]
    
    # Get features ordered by the order field
    features = solution.features.all().order_by('order')
    
    context = {
        'solution': solution,
        'features': features,
        'related_solutions': related_solutions,
    }
    
    return render(request, 'solutions/solution_detail.html', context)

def share_solution(request, slug):
    """
    Handle sharing a solution through email or social media
    This is a placeholder and would need integration with email services or social APIs
    """
    solution = get_object_or_404(Solution, slug=slug, is_active=True)
    
    if request.method == 'POST':
        # Process share form (this would need to be implemented)
        messages.success(request, f"Thank you for sharing {solution.name}!")
        return redirect('solutions:solution_detail', slug=slug)
    
    return render(request, 'solutions/share_solution.html', {'solution': solution})