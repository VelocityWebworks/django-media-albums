# Django Media Albums

[![Build Status](https://travis-ci.org/VelocityWebworks/django-media-albums.svg?branch=master)](https://travis-ci.org/VelocityWebworks/django-media-albums)

This app is used to create albums consisting of any combination of the
following:

* Photos
* Video files
* Audio files

This app also optionally allows regular (non-staff) users to upload photos.

This app requires Django 1.8, 1.9, 1.10, or 1.11.

## Installation

### Step 1 of 5: Install the required packages

Install using pip:

```bash
pip install django-media-albums
```

If you will be using the templates that come with this app, also install these
packages using pip:

```bash
pip install django-bootstrap-pagination sorl-thumbnail
```

If you will be allowing regular (non-staff) users to upload photos and will be
using the `upload.html` template that comes with this app, also install the
`django-crispy-forms` package using pip:

```bash
pip install django-crispy-forms
```

### Step 2 of 5: Update `settings.py`

Make sure the following settings are all configured the way you want them in
your `settings.py`:

```
MEDIA_ROOT
MEDIA_URL
STATIC_ROOT
STATIC_URL
```

If you will be allowing regular (non-staff) users to upload photos, you will
also need to have the `DEFAULT_FROM_EMAIL` setting present in your
`settings.py` (for the notification email that gets sent out when a user
uploads a photo).

Add `'media_albums'` to your `settings.py` INSTALLED_APPS:

```python
INSTALLED_APPS = (
    ...
    'media_albums',
    ...
)
```

If you will be using the templates that come with this app, also add the
following to your `settings.py` INSTALLED_APPS:

```python
INSTALLED_APPS = (
    ...
    'bootstrap_pagination',
    'sorl.thumbnail',
    ...
)
```

If you will be allowing regular (non-staff) users to upload photos and will be
using the `upload.html` template that comes with this app, also add
`'crispy_forms'` to your `settings.py` INSTALLED_APPS and make sure the
`CRISPY_TEMPLATE_PACK` setting is configured the way you want it:

```python
INSTALLED_APPS = (
    ...
    'crispy_forms',
    ...
)

CRISPY_TEMPLATE_PACK = 'bootstrap3'
```

If you will be enabling audio and/or video and will be using the templates that
come with this app, also enable the
`'django.template.context_processors.media'` context processor:

```python
TEMPLATES = [
    ...
    {
        ...
        'OPTIONS': {
            ...
            'context_processors': [
                ...
                'django.template.context_processors.media',
                ...
            ],
            ...
        },
        ...
    },
    ...
]
```

### Step 3 of 5: Update `urls.py`

Create a URL pattern in your `urls.py`:

```python
from django.conf.urls import include, url

urlpatterns = [
    ...
    url(r'^media-albums/', include('media_albums.urls')),
    ...
]
```

### Step 4 of 5: Add the database tables

Run the following command:

```bash
python manage.py migrate
```

### Step 5 of 5: Update your project's `base.html` template (if necessary)

If you will be using the templates that come with this app, make sure your
project has a `base.html` template and that it has these blocks:

```
content
extra_styles
```

## Configuration

To override any of the default settings, create a dictionary named
`MEDIA_ALBUMS` in your `settings.py` with each setting you want to override.
For example, if you wanted to enable audio and video, but leave all of the
other settings alone, you would add this to your `settings.py`:

```python
MEDIA_ALBUMS = {
    'audio_files_enabled': True,
    'video_files_enabled': True,
}
```

These are the settings:

### `photos_enabled` (default: `True`)

When set to `True`, albums may contain photos.

### `audio_files_enabled` (default: `False`)

When set to `True`, albums may contain audio files.

### `audio_files_format1_extension` (default: `'mp3'`)

When an audio file is uploaded, the "Audio file 1" field must have this
extension. To allow multiple extensions, make this string a comma separated
list. This setting is only relevant if `audio_files_enabled` is set to `True`.

### `audio_files_format2_extension` (default: `'ogg'`)

When an audio file is uploaded, the "Audio file 2" field must have this
extension. To allow multiple extensions, make this string a comma separated
list. This setting is only relevant if `audio_files_enabled` is set to `True`.

### `audio_files_format2_required` (default: `False`)

When set to `True`, the "Audio file 2" field will be marked as required. This
setting is only relevant if `audio_files_enabled` is set to `True`.

### `video_files_enabled` (default: `False`)

When set to `True`, albums may contain video files.

### `video_files_format1_extension` (default: `'mp4'`)

When a video file is uploaded, the "Video file 1" field must have this
extension. To allow multiple extensions, make this string a comma separated
list. This setting is only relevant if `video_files_enabled` is set to `True`.

### `video_files_format2_extension` (default: `'webm'`)

When a video file is uploaded, the "Video file 2" field must have this
extension. To allow multiple extensions, make this string a comma separated
list. This setting is only relevant if `video_files_enabled` is set to `True`.

### `video_files_format2_required` (default: `False`)

When set to `True`, the "Video file 2" field will be marked as required. This
setting is only relevant if `video_files_enabled` is set to `True`.

### `user_uploaded_photos_enabled` (default: `False`)

When set to `True`, regular (non-staff) users may upload photos. However, they
still must be approved by a staff user.

### `user_uploaded_photos_login_required` (default: `True`)

When set to `True`, regular (non-staff) users may only upload photos if they
are logged in. This setting is only relevant if `user_uploaded_photos_enabled`
is set to `True`.

### `user_uploaded_photos_album_name` (default: `'User Photos'`)

When a staff user approves a photo uploaded by a regular (non-staff) user, the
photo will be added to the album with this name. This setting is only relevant
if `user_uploaded_photos_enabled` is set to `True`.

### `user_uploaded_photos_album_slug` (default: `'user-photos'`)

When a staff user approves a photo uploaded by a regular (non-staff) user, the
photo will be added to the album with this slug. This setting is only relevant
if `user_uploaded_photos_enabled` is set to `True`.

### `paginate_by` (default: `10`)

This setting determines how many items can be on a single page. This applies to
the list of albums as well as the list of items within albums.
