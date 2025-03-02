from django.db import models
from horizon.utils.utils import HTMLConverter
# horizon/models.py
import os
from PIL import Image
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import uuid
import re


class Type(models.Model):
    # Used to identify the type of content
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    

class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    # Used to set Category
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Author(models.Model):
    first_name = models.CharField(max_length=100, blank=False, null=False)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    profile_image = models.URLField(blank=True, null=True)  # Stores image URL
    profile_image_srcset = models.JSONField(blank=True, null=True, default=dict)  # Dynamic srcset field
    description = models.TextField()

    def __str__(self):
        return f"{self.first_name} {self.middle_name + ' ' if self.middle_name else ''}{self.last_name}"
    
    def get_profile_srcset(self):
        """
        Returns a properly formatted `srcset` attribute string for the profile image.
        Expects `profile_image_srcset` to be a dictionary like:
        {
            "https://example.com/small.jpg": "480w",
            "https://example.com/medium.jpg": "768w",
            "https://example.com/large.jpg": "1200w"
        }
        """
        if not self.profile_image_srcset:
            return ""

        return ", ".join([f"{url} {width}" for url, width in self.profile_image_srcset.items()])
    
    def get_html_description(self):
        converter = HTMLConverter()
        return converter.get_html(self.description)



class Content(models.Model):    
    # SEO stuff
    meta_title = models.CharField(max_length=255, null=False, blank=False, default="")
    meta_description = models.CharField(max_length=255, null=False, blank=False, default="")
    slug = models.SlugField(unique=True, null=False, blank=False, db_index=True)

    # Content Management. Type, Cateogory, Tags... etc
    type = models.ForeignKey(
        Type,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="contents"
    )

    categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name="contents"
    )

    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="contents"
    )
    
    # Author Relationship (One author -> Many content)
    author = models.ForeignKey(Author, on_delete=models.PROTECT, related_name="contents")

    
    # Page content
    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.CharField(max_length=255, null=False, blank=False, default="")
    published_at = models.DateTimeField(auto_now_add=True) # Set only once when created
    updated_at = models.DateTimeField(auto_now=True) # Auto-updates on every save
    read_time = models.IntegerField(default=1, null=False, blank=False)
    body = models.TextField()
    html_body = models.TextField(blank=True, null=True) # Precomputed for Performance

    # featured image
    image_featured = models.URLField(blank=True, null=True)  # Stores image URL
    image_featured_srcset = models.JSONField(blank=True, null=True, default=dict)  # Dynamic srcset field
    image_caption = models.CharField(max_length=255, null=False, blank=False, default="")
    image_by = models.CharField(max_length=255, null=False, blank=False, default="")

    # Publish status
    publish = models.BooleanField(default=False)

    # image_featured_srcset
    # {
    #     "https://example.com/small.jpg": "480w",
    #     "https://example.com/medium.jpg": "768w",
    #     "https://example.com/large.jpg": "1200w",
    # }


    def __str__(self):
        return f"{self.title}"
    

    def get_html_content(self):
        converter = HTMLConverter()
        return converter.get_html(self.body)
    

    def get_srcset(self):
        """
        Returns a properly formatted `srcset` attribute string if additional image sizes exist.
        Expects `image_srcset` to be a dictionary like { "https://example.com/small.jpg": "480w", ... }
        """
        if not self.image_featured_srcset:
            return ""

        return ", ".join([f"{url} {width}" for url, width in self.image_featured_srcset.items()])

    

    def save(self, *args, **kwargs):
        """
        Override the save method to update `html_body` only when `body` is changed.
        """
        if self.body:  # Ensure body is not empty
            self.html_body = self.get_html_content()  # Precompute HTML version
        
        super().save(*args, **kwargs)  # Call Django's default save method


def validate_jpg_and_size(file):
    # Check file extension (only allow .jpg)
    ext = os.path.splitext(file.name)[1].lower()
    if ext != '.jpg':
        raise ValidationError('Only .jpg files are allowed.')
    
    # Check file size (less than 200kB)
    max_size = 200 * 1024  # 200kB in bytes
    if file.size > max_size:
        raise ValidationError('Image file too large (maximum 200kB allowed).')


def image_upload_to(instance, filename):
    """
    Generates a unique folder for each upload and returns the full file path.
    """
    unique_folder = uuid.uuid4().hex  # Generate a unique folder name.
    folder_path = f'images/{unique_folder}'
    return f'{folder_path}/{filename}'


class UploadedImage(models.Model):
    title = models.CharField(max_length=200, blank=True)
    # uploaded_to = models.CharField(max_length=500, editable=False, blank=True) # Auto populates in "image_upload_to" method
    image = models.ImageField(
        upload_to=image_upload_to, 
        validators=[validate_jpg_and_size]
    )

    def save(self, *args, **kwargs):
        # Save the original image first.
        super().save(*args, **kwargs)
        
        # Define the target widths.
        widths = [100, 400, 800, 1200, 1600]
        
        # Open the image to determine its original dimensions.
        with Image.open(self.image.path) as img:
            orig_width, orig_height = img.size
        
        # Generate resized versions for each target width.
        for width in widths:
            # Calculate the new height preserving the aspect ratio.
            new_height = int(orig_height * width / orig_width)
            new_size = (width, new_height)
            self._create_resized_image(new_size)


    def _create_resized_image(self, size):
        """
        Creates a resized version of the original image.
        The resized image is stored in the same folder as the original image,
        with a filename suffix indicating its dimensions.
        """
        # Full path to the original image.
        orig_path = self.image.path
        # Get the folder where the image is stored.
        folder = os.path.dirname(orig_path)
        # Get the base filename (without extension) and the extension.
        base, ext = os.path.splitext(os.path.basename(orig_path))
        # Construct the filename for the resized image.
        resized_filename = f"{base}_{size[0]}x{size[1]}{ext}"
        resized_path = os.path.join(folder, resized_filename)

        quality = 50
        if size[0] == 100:
            quality = 100
        
        if size[0] == 400:
            quality = 80
        
        # If the resized file doesn't already exist, create it.
        if not os.path.exists(resized_path):
            try:
                with Image.open(orig_path) as img:
                    # Resize using a high-quality downsampling filter.
                    resized_img = img.resize(size, Image.Resampling.LANCZOS)
                    resized_img.save(resized_path, quality=quality)
            except Exception as e:
                # Optionally log the error here.
                print(f"[IMAGE][_create_resized_image] exception={str(e)}")
                pass


    def available_resized_images(self):
        """
        Scans the folder where the original image is stored and returns a comma-separated list
        of all file names that match the resized image pattern. Here, it simply lists all files
        in the same folder that start with the original base filename followed by an underscore.
        """
        try:
            # Get the folder where the image is stored.
            image_folder = os.path.dirname(self.image.path)
            # Get the base filename (without extension) of the original image.
            base_filename, _ = os.path.splitext(os.path.basename(self.image.path))
            # List all files in the folder that start with the base filename plus an underscore.
            all_files = os.listdir(image_folder)
            resized_files = [filename for filename in all_files if filename.startswith(f"{base_filename}_")]
            return '\n'.join(resized_files)
        except Exception as e:
            # Optionally log the error.
            return f"[IMAGE] ERROR: {str(e)}"
    available_resized_images.short_description = "Available Sizes"

    # # USED IN ADMIN
    # def get_uploaded_folder(self):
    #     return self.uploaded_to
    # get_uploaded_folder.short_description = "Upload Folder"

    def __str__(self):
        return self.title or f"Image {self.pk}"
