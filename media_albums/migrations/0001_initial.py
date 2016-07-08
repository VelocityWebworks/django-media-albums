# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200, verbose_name='name')),
                ('slug', models.SlugField(unique=True, verbose_name='slug')),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('visibility', models.CharField(max_length=8, verbose_name='visibility', choices=[(b'public', 'Public'), (b'unlisted', 'Unlisted - this album will not be shown in the list of albums, but anybody who has the URL will be able to view it'), (b'private', 'Private - this album will not be shown in the list of albums, but staff users will be able to view it')])),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('ordering', models.IntegerField(default=0, help_text='Override automatic ordering.', verbose_name='ordering')),
            ],
            options={
                'ordering': ('ordering', 'name'),
                'verbose_name': 'album',
                'verbose_name_plural': 'albums',
            },
        ),
        migrations.CreateModel(
            name='AudioFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('ordering', models.IntegerField(default=0, help_text='Override automatic ordering.', verbose_name='ordering', db_index=True)),
                ('caption', models.CharField(help_text='A brief caption describing the audio.', max_length=255, verbose_name='caption', blank=True)),
                ('description', models.TextField(help_text='A more in-depth description of the audio.', verbose_name='description', blank=True)),
                ('audio_file_1', models.FileField(help_text='Use this field to upload the audio in mp3 format.', upload_to=b'media_albums/%Y/%m/%d/audio', verbose_name='audio file 1')),
                ('audio_file_2', models.FileField(help_text='Use this field to upload the same audio in ogg format. Having the same audio in a second format will allow more web browsers to be able to play the audio file.', upload_to=b'media_albums/%Y/%m/%d/audio', verbose_name='audio file 2', blank=True)),
                ('cover_art', models.ImageField(help_text='The image to display below the audio player.', upload_to=b'media_albums/%Y/%m/%d/audio', verbose_name='cover art', blank=True)),
                ('album_photo', models.BooleanField(default=False, help_text='Use the cover art as the album photo.', verbose_name='album photo')),
                ('album', models.ForeignKey(to='media_albums.Album')),
            ],
            options={
                'ordering': ('ordering', 'name'),
                'abstract': False,
                'verbose_name': 'audio file',
                'verbose_name_plural': 'audio files',
            },
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('ordering', models.IntegerField(default=0, help_text='Override automatic ordering.', verbose_name='ordering', db_index=True)),
                ('caption', models.CharField(help_text='A brief caption describing the photo.', max_length=255, verbose_name='caption', blank=True)),
                ('description', models.TextField(help_text='A more in-depth description of the photo.', verbose_name='description', blank=True)),
                ('image', models.ImageField(upload_to=b'media_albums/%Y/%m/%d/photo', verbose_name='image')),
                ('album_photo', models.BooleanField(default=False, help_text='Use this photo as the album photo.', verbose_name='album photo')),
            ],
            options={
                'ordering': ('ordering', 'name'),
                'abstract': False,
                'verbose_name': 'photo',
                'verbose_name_plural': 'photos',
            },
        ),
        migrations.CreateModel(
            name='VideoFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('ordering', models.IntegerField(default=0, help_text='Override automatic ordering.', verbose_name='ordering', db_index=True)),
                ('caption', models.CharField(help_text='A brief caption describing the video.', max_length=255, verbose_name='caption', blank=True)),
                ('description', models.TextField(help_text=b'A more in-depth description of the video.', verbose_name='description', blank=True)),
                ('video_file_1', models.FileField(help_text='Use this field to upload the video in mp4 format.', upload_to=b'media_albums/%Y/%m/%d/video', verbose_name='video file 1')),
                ('video_file_2', models.FileField(help_text='Use this field to upload the same video in webm format. Having the same video in a second format will allow more web browsers to be able to play the video file.', upload_to=b'media_albums/%Y/%m/%d/video', verbose_name='video file 2', blank=True)),
                ('poster', models.ImageField(help_text="The image to use for the poster frame (the poster frame is what shows until the user plays or seeks). If you leave this blank, nothing is displayed until the video's first frame is available; then the first frame is shown as the poster frame.", upload_to=b'media_albums/%Y/%m/%d/video', verbose_name='poster', blank=True)),
                ('album_photo', models.BooleanField(default=False, help_text='Use the poster as the album photo.', verbose_name='album photo')),
                ('album', models.ForeignKey(to='media_albums.Album')),
            ],
            options={
                'ordering': ('ordering', 'name'),
                'abstract': False,
                'verbose_name': 'video file',
                'verbose_name_plural': 'video files',
            },
        ),
        migrations.CreateModel(
            name='UserPhoto',
            fields=[
                ('photo_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='media_albums.Photo')),
                ('added_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('ordering', 'name'),
                'abstract': False,
            },
            bases=('media_albums.photo',),
        ),
        migrations.AddField(
            model_name='photo',
            name='album',
            field=models.ForeignKey(to='media_albums.Album'),
        ),
    ]
