import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'streamer_project.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = 'kelly'
email = 'wafulakelly45@.com'
password = 'root'

if not User.objects.filter(username=username).exists():
    print(f"Creating superuser account for {username}...")
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superuser created successfully!")
else:
    print(f"Superuser {username} already exists.")
