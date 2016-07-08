from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import AudioFile, Photo, UserPhoto, VideoFile
from .settings import MEDIA_ALBUMS_SETTINGS


class AudioFileForm(forms.ModelForm):
    class Meta:
        model = AudioFile
        fields = [
            'album',
            'name',
            'ordering',
            'caption',
            'description',
            'audio_file_1',
            'audio_file_2',
            'cover_art',
            'album_photo',
        ]

    def __init__(self, *args, **kwargs):
        super(AudioFileForm, self).__init__(*args, **kwargs)

        if MEDIA_ALBUMS_SETTINGS['audio_files_format2_required']:
            self.fields['audio_file_2'].required = True


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = [
            'album',
            'name',
            'ordering',
            'caption',
            'description',
            'image',
            'album_photo',
        ]


class UserPhotoForm(forms.ModelForm):
    class Meta:
        model = UserPhoto
        fields = [
            'name',
            'caption',
            'description',
            'image',
        ]

    def __init__(self, *args, **kwargs):
        super(UserPhotoForm, self).__init__(*args, **kwargs)
        self.fields['name'].help_text = _('The name of the photo.')


class VideoFileForm(forms.ModelForm):
    class Meta:
        model = VideoFile
        fields = [
            'album',
            'name',
            'ordering',
            'caption',
            'description',
            'video_file_1',
            'video_file_2',
            'poster',
            'album_photo',
        ]

    def __init__(self, *args, **kwargs):
        super(VideoFileForm, self).__init__(*args, **kwargs)

        if MEDIA_ALBUMS_SETTINGS['video_files_format2_required']:
            self.fields['video_file_2'].required = True
