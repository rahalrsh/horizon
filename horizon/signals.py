import os
import shutil
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import UploadedImage

# Register this in apps.py
@receiver(post_delete, sender=UploadedImage)
def delete_uploaded_folder(sender, instance, **kwargs):
    """
    Deletes the entire folder where the image and its resized versions are stored.
    This signal is triggered after an UploadedImage instance is deleted.
    """
    image_folder = os.path.dirname(instance.image.path)
    if os.path.exists(image_folder):
        shutil.rmtree(image_folder)
