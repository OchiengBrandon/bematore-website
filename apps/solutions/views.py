from django.shortcuts import render, get_object_or_404
from .models import Solution

def solution_list(request):
    solutions = Solution.objects.filter(is_active=True).order_by('order')
    return render(request, 'solutions/solution_list.html', {'solutions': solutions})

def solution_detail(request, slug):
    solution = get_object_or_404(Solution, slug=slug)
    return render(request, 'solutions/solution_detail.html', {'solution': solution})