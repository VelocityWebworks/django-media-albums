from django.test import TestCase
from django.test.utils import override_settings

from ..models import Album, AudioFile, VideoFile
from ..templatetags import media_albums_tags
from ..settings import compute_settings


class TemplateTagsTest(TestCase):
    fixtures = [
        'media_albums_test_data.json',
    ]

    def test_get_mime_type(self):
        compute_settings()

        audio_file = AudioFile.objects.get(pk=1)
        self.assertEqual(
            media_albums_tags.get_mime_type(audio_file, 'audio_file_1'),
            'audio/ogg'
        )
        self.assertEqual(
            media_albums_tags.get_mime_type(audio_file, 'audio_file_2'),
            'audio/mpeg'
        )

        video_file = VideoFile.objects.get(pk=1)
        self.assertEqual(
            media_albums_tags.get_mime_type(video_file, 'video_file_1'),
            'video/mp4'
        )
        self.assertEqual(
            media_albums_tags.get_mime_type(video_file, 'video_file_2'),
            'video/webm'
        )

    def test_get_album_items(self):
        compute_settings()

        tests = [
            # Public album
            {
                'album_name': 'Cat Photos',
                'expected_total': 10,
            },
            # Unlisted album
            {
                'album_name': 'Funny Animated GIFs',
                'expected_total': 5,
            },
            # Private album
            {
                'album_name': 'Miscellaneous',
                'expected_total': 1,
            },
        ]

        for test in tests:
            album_items = media_albums_tags.get_album_items(test['album_name'])
            self.assertEqual(len(album_items), test['expected_total'])

            for album_item in album_items:
                self.assertEqual(album_item.album.name, test['album_name'])

    @override_settings(MEDIA_ALBUMS={
        'audio_files_enabled': True,
        'video_files_enabled': True,
    })
    def test_get_album_items_audio_and_video_enabled(self):
        compute_settings()

        tests = [
            # Public album
            {
                'album_name': 'Cat Photos',
                'expected_total': 10,
            },
            # Unlisted album
            {
                'album_name': 'Funny Animated GIFs',
                'expected_total': 5,
            },
            # Private album
            {
                'album_name': 'Miscellaneous',
                'expected_total': 3,
            },
        ]

        for test in tests:
            album_items = media_albums_tags.get_album_items(test['album_name'])
            self.assertEqual(len(album_items), test['expected_total'])

            for album_item in album_items:
                self.assertEqual(album_item.album.name, test['album_name'])

    def test_next_previous_object(self):
        compute_settings()

        album = Album.objects.get(slug='miscellaneous')
        items = album.items

        next_previous_item_0 = media_albums_tags.next_previous_object(
            items[0]
        )
        self.assertEqual(next_previous_item_0['next'], items[0])
        self.assertEqual(next_previous_item_0['previous'], items[0])

    @override_settings(MEDIA_ALBUMS={
        'audio_files_enabled': True,
        'video_files_enabled': True,
    })
    def test_next_previous_object_audio_and_video_enabled(self):
        compute_settings()

        album = Album.objects.get(slug='miscellaneous')
        items = album.items

        next_previous_item_0 = media_albums_tags.next_previous_object(items[0])
        self.assertEqual(next_previous_item_0['next'], items[1])
        self.assertEqual(next_previous_item_0['previous'], items[2])

        next_previous_item_1 = media_albums_tags.next_previous_object(items[1])
        self.assertEqual(next_previous_item_1['next'], items[2])
        self.assertEqual(next_previous_item_1['previous'], items[0])

        next_previous_item_2 = media_albums_tags.next_previous_object(items[2])
        self.assertEqual(next_previous_item_2['next'], items[0])
        self.assertEqual(next_previous_item_2['previous'], items[1])
