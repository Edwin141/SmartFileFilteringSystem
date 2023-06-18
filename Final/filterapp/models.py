from django.db import models

class FileInfo(models.Model):
    filename = models.TextField()
    content = models.TextField()
    file_type = models.TextField()
    tags = models.TextField()
    file_path = models.TextField()

    def __str__(self):
        return self.filename
    
    class Meta:
        db_table = 'files'  # Set the table name to match the one in your SQLite database