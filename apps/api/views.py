from django.shortcuts import render, get_object_or_404
from .models import APIKey, APILog

def api_key_list(request):
    api_keys = APIKey.objects.all()
    return render(request, 'api/api_key_list.html', {'api_keys': api_keys})

def api_key_detail(request, pk):
    api_key = get_object_or_404(APIKey, pk=pk)
    return render(request, 'api/api_key_detail.html', {'api_key': api_key})

def api_log_list(request):
    api_logs = APILog.objects.all()
    return render(request, 'api/api_log_list.html', {'api_logs': api_logs})