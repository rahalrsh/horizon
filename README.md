# HOW TO RUN
- python manage.py runserver
- ./tailwindcss -i ./horizon/static/input_tailwind.css -o horizon/static/tailwind.css --watch

- python manage.py makemigrations
- python manage.py migrate




# INSTALLATION STEPS
mkdir horizon
cd horizon
python3 -m venv venv
source venv/bin/activate
pip install django
pip freeze > requirements.txt
django-admin startproject horizon_core .

# Lets create the actual app/module
python manage.py startapp horizon

# RUN SERVER
python manage.py runserver

# Create initial database tables
python manage.py migrate

# CREATE SUPER USER
python manage.py createsuperuser
    - rahal
    - rahal@horizon.com
    - 1234



# installing tailwind (via standalone CLI, no nodejs, no npm)
    - https://www.youtube.com/watch?v=qoOUTtELHbk&ab_channel=BugBytes
    - https://tailwindcss.com/blog/standalone-cli


    # grab the executable
    curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-arm64
    chmod +x tailwindcss-macos-arm64
    mv tailwindcss-macos-arm64 tailwindcss

    # Create a tailwind.config.js file
    # ./tailwindcss init
    create input_tailwind.css in horizon/static/input_tailwind.css
    # Start a watcher
    ./tailwindcss -i ./horizon/static/input_tailwind.css -o horizon/static/tailwind.css --watch
    # For production - Compile and minify your CSS
    ./tailwindcss -i ./horizon/static/input_tailwind.css -o horizon/static/tailwind.css --minify



# (NOT USED/ALL REMOVED) Installing TinyMCE
 - pip install django-tinymce  
 - add 'tinymce', in settings.py to INSTALLED_APPS
 - add TINYMCE_DEFAULT_CONFIG in settings.py
 - add path('tinymce/', include('tinymce.urls')), in urls.py
 - updte models to include HTMLField
 - update admin model with new class ContentForm. This ensures only one field ("body") is using tinymce


# CREATE A MIGRATION MANUALY
- python manage.py makemigrations your_app_name --empty --name migrate_category_data


# IMAGE UPLOAD
- pip install Pillow
- in models.py: Add UploadedImage method
<!-- - in views.py: Add serve_pre_resized_image -->
<!-- - in urls.py: add path name='serve_pre_resized_image' -->
- in settings.py: Set MEDIA_URL and MEDIA_ROOT
- add signals.py and register in apps.py amd __init__py

