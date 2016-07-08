from django.conf import settings

default_settings = {
    'photos_enabled': True,
    'audio_files_enabled': False,
    'audio_files_format1_extension': 'mp3',
    'audio_files_format2_extension': 'ogg',
    'audio_files_format2_required': False,
    'video_files_enabled': False,
    'video_files_format1_extension': 'mp4',
    'video_files_format2_extension': 'webm',
    'video_files_format2_required': False,
    'user_uploaded_photos_enabled': False,
    'user_uploaded_photos_login_required': True,
    'user_uploaded_photos_album_name': 'User Photos',
    'user_uploaded_photos_album_slug': 'user-photos',
    'paginate_by': 10,
}

MEDIA_ALBUMS_SETTINGS = {}


def compute_settings():
    for name, value in default_settings.items():
        MEDIA_ALBUMS_SETTINGS[name] = value

    if hasattr(settings, 'MEDIA_ALBUMS'):
        MEDIA_ALBUMS_SETTINGS.update(settings.MEDIA_ALBUMS)

compute_settings()
