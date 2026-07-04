import os
import re
from django.shortcuts import render, get_object_or_404
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Video

def video_list(request):
    videos = Video.objects.all().order_by('-uploaded_at')
    return render(request, 'videos/video_list.html', {'videos': videos})

def video_detail(request, pk):
    video = get_object_or_404(Video, pk=pk)
    return render(request, 'videos/video_detail.html', {'video': video})

@csrf_exempt
def upload_videos(request):
    if request.method == 'POST' and request.FILES.getlist('files'):
        files = request.FILES.getlist('files')
        uploaded_videos = []
        
        for file in files:
            # Extract name and clean it up (e.g., "my_video.mp4" -> "my video")
            raw_name = file.name
            clean_name = os.path.splitext(raw_name)[0].replace('_', ' ').replace('-', ' ')
            
            # Create and save the video instance
            video = Video.objects.create(
                title=clean_name,
                description=f"Automatically processed upload of {raw_name}.",
                video_file=file
            )
            uploaded_videos.append({'id': video.id, 'title': video.title})
            
        return JsonResponse({'status': 'success', 'videos': uploaded_videos})
        
    return render(request, 'videos/upload.html')

def stream_video(request, pk):
    video = get_object_or_404(Video, pk=pk)
    path = video.video_file.path
    
    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_match = re.match(r'bytes=\s*(\d+)-(\d*)', range_header)
    size = os.path.getsize(path)
    content_type = 'video/mp4'

    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        last_byte = int(last_byte) if last_byte else size - 1
        if last_byte >= size:
            last_byte = size - 1
        length = last_byte - first_byte + 1
        
        def file_iterator():
            with open(path, 'rb') as f:
                f.seek(first_byte)
                remaining = length
                while remaining > 0:
                    chunk_size = min(1024 * 8, remaining)
                    data = f.read(chunk_size)
                    if not data:
                        break
                    remaining -= len(data)
                    yield data

        response = StreamingHttpResponse(file_iterator(), status=206, content_type=content_type)
        response['Content-Range'] = f'bytes {first_byte}-{last_byte}/{size}'
        response['Accept-Ranges'] = 'bytes'
        response['Content-Length'] = str(length)
    else:
        def file_iterator():
            with open(path, 'rb') as f:
                while True:
                    data = f.read(1024 * 8)
                    if not data:
                        break
                    yield data

        response = StreamingHttpResponse(file_iterator(), content_type=content_type)
        response['Accept-Ranges'] = 'bytes'
        response['Content-Length'] = str(size)

    return response

from django.core.management import call_command
from django.http import HttpResponse, Http404

def run_remote_migrations(request):
    # Change 'mysecretkey123' to any private password you want
    secret_token = request.GET.get('token')
    if secret_token != 'mysecretkey123':
        raise Http404("Page not found")  # Hide the page from the public
        
    try:
        # Programmatically execute: python manage.py migrate
        call_command('migrate', interactive=False)
        return HttpResponse("🚀 Migrations executed successfully on the remote database!", content_type="text/plain")
    except Exception as e:
        return HttpResponse(f"❌ Migration failed: {str(e)}", status=500, content_type="text/plain")
