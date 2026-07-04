import os
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, StreamingHttpResponse
from django.core.management import call_command
from .models import Video

def video_list(request):
    videos = Video.objects.all().order_by('-uploaded_at')
    return render(request, 'videos/video_list.html', {'videos': videos})

def upload_videos(request):
    if request.method == 'POST':
        # Safely extract list from multi-file input key array
        files = request.FILES.getlist('video_files')
        
        for f in files:
            # Drop dangerous shell symbols out of file strings
            clean_name = re.sub(r'[^a-zA-Z0-9._-]', '_', f.name)
            
            video = Video(
                title=clean_name.rsplit('.', 1)[0].replace('_', ' '),
                description="Uploaded locally via multi-upload portal."
            )
            # Save payload to local hard drive media directory directly
            video.video_file.save(clean_name, f, save=True)
            
        return HttpResponse("Success", content_type="text/plain")
        
    return render(request, 'videos/upload.html')

def stream_video(request, pk):
    video = get_object_or_404(Video, pk=pk)
    path = video.video_file.path

    # Stop 500 crashes if file is lost due to an ephemeral server reset
    if not os.path.exists(path):
        return HttpResponse(
            "<div style='font-family:sans-serif; padding:20px; color:#cc0000;'>"
            "<h3>⚠️ File Missing from Temporary Render Storage</h3>"
            "<p>Render automatically flushes local disk data during restarts. "
            "Please remove this broken reference via Admin and upload your video again!</p>"
            "</div>",
            status=404
        )

    def file_iterator(file_name, chunk_size=8192):
        with open(file_name, 'rb') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    size = os.path.getsize(path)
    response = StreamingHttpResponse(file_iterator(path), content_type='video/mp4')
    response['Content-Length'] = size
    response['Accept-Ranges'] = 'bytes'
    return response

def run_remote_migrations(request):
    secret_token = request.GET.get('token')
    if secret_token != 'mysecretkey123':
        raise Http404("Page not found")
    try:
        call_command('migrate', interactive=False)
        return HttpResponse("🚀 Migrations executed successfully!", content_type="text/plain")
    except Exception as e:
        return HttpResponse(f"❌ Migration failed: {str(e)}", status=500, content_type="text/plain")