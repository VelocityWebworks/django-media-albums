from django import template

from ..models import Album, AudioFile, Photo, VideoFile
from ..settings import MEDIA_ALBUMS_SETTINGS

register = template.Library()


@register.simple_tag
def get_mime_type(obj=None, field=None):
    mime_types = {
        'audio': {
            'm4a': 'audio/mp4',
            'mp3': 'audio/mpeg',
            'ogg': 'audio/ogg',
        },
        'video': {
            'mp4': 'video/mp4',
            'ogv': 'video/ogg',
            'webm': 'video/webm',
        },
    }

    mime_type = ''

    if obj and field:
        item_type = None

        try:
            if obj.is_audio:
                item_type = 'audio'
            if obj.is_video:
                item_type = 'video'
        except AttributeError:
            pass

        if item_type:
            ext = None

            try:
                if hasattr(obj, field):
                    ext = getattr(obj, field).name.rsplit('.', 1)[-1].lower()
            except TypeError:
                pass

            if ext is not None and ext in mime_types[item_type]:
                mime_type = mime_types[item_type][ext]

    return mime_type


@register.assignment_tag
def get_album_items(album_name=None):
    if album_name:
        try:
            album = Album.objects.get(
                name=album_name,
            )
        except Album.DoesNotExist:
            return None

        return album.items
    else:
        return None


@register.assignment_tag
def next_previous_object(media_albums_object):
    mao = media_albums_object
    album = mao.album
    album_items = []

    if MEDIA_ALBUMS_SETTINGS['photos_enabled']:
        for obj in Photo.objects.filter(
            album=album,
        ).order_by('ordering', 'name'):
            album_items.append(obj)

    if MEDIA_ALBUMS_SETTINGS['video_files_enabled']:
        for obj in VideoFile.objects.filter(
            album=album,
        ).order_by('ordering', 'name'):
            album_items.append(obj)

    if MEDIA_ALBUMS_SETTINGS['audio_files_enabled']:
        for obj in AudioFile.objects.filter(
            album=album,
        ).order_by('ordering', 'name'):
            album_items.append(obj)

    total_album_items = len(album_items)

    current_item_position = album_items.index(mao)

    if current_item_position + 1 < total_album_items:
        next_item_position = current_item_position + 1
    else:
        next_item_position = 0

    if current_item_position - 1 >= 0:
        previous_item_position = current_item_position - 1
    else:
        previous_item_position = total_album_items - 1

    return {
        'next': album_items[next_item_position],
        'previous': album_items[previous_item_position],
        'current_item_position': current_item_position + 1,
        'next_item_position': next_item_position + 1,
        'previous_item_position': previous_item_position + 1,
        'total_album_items': total_album_items,
    }
