import uuid
import os
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

User = get_user_model()

def validate_audio_file_size(file):
    max_size_mb = 5
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f'File size cannot exceed {max_size_mb}MB')

def audio_file_path(instance, filename):
    # Get the file extension
    ext = os.path.splitext(filename)[1]
    # Generate a random UUID filename
    filename = f"{uuid.uuid4()}{ext}"
    # Return the path: audio_files/uuid.ext
    return os.path.join('audio_files', filename)

class AudioFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audio_files')
    file = models.FileField(
        upload_to=audio_file_path,  # Changed from string to function
        validators=[
            FileExtensionValidator(allowed_extensions=['mp3', 'wav', 'ogg', 'flac', 'm4a']),
            validate_audio_file_size
        ]
    )
    title = models.CharField(max_length=60)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title or self.file.name}"
    
    def delete(self, *args, **kwargs):
        # Delete the file from storage when model is deleted
        self.file.delete(save=False)
        super().delete(*args, **kwargs)