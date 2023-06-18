import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartfilefilter.settings')
django.setup()

from filterapp.models import FileInfo

for file_info in FileInfo.objects.all():
    # Replace the part of the file path that comes before 'static'
    new_path = os.path.join('/static', 'StoredFiles', os.path.basename(file_info.file_path))
    file_info.file_path = new_path.replace('\\', '/')
    file_info.save()
