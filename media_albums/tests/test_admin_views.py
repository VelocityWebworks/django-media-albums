try:
    from importlib import reload
except ImportError:
    pass

from django.contrib.auth import get_user_model
from django.core.urlresolvers import NoReverseMatch, clear_url_caches, reverse
from django.test import TestCase
from django.test.utils import override_settings

from ..models import Album, UserPhoto

from .. import admin as media_albums_admin
from ..settings import compute_settings
from . import urls as test_urls


class ViewsTest(TestCase):
    fixtures = [
        'media_albums_test_data.json',
    ]

    def reload(self):
        compute_settings()
        reload(media_albums_admin)
        clear_url_caches()
        reload(test_urls)

    def setUp(self):
        credentials = {
            'username': 'staff_user',
            'password': 'testing!',
        }

        staff_user = get_user_model()._default_manager.create_user(
            username=credentials['username'],
            password=credentials['password'],
            email='superuser@example.com',
            first_name='Super',
            last_name='User',
        )

        staff_user.is_staff = True
        staff_user.is_superuser = True
        staff_user.save()

        self.client.login(
            username=credentials['username'],
            password=credentials['password'],
        )

    def test_album_views(self):
        self.reload()

        tests = [
            {
                'url': 'admin:media_albums_album_changelist',
                'url_args': [],
            },
            {
                'url': 'admin:media_albums_album_add',
                'url_args': [],
            },
            {
                'url': 'admin:media_albums_album_change',
                'url_args': [1],
            },
            {
                'url': 'admin:media_albums_album_delete',
                'url_args': [1],
            },
        ]

        for test in tests:
            url = reverse(test['url'], args=test['url_args'])
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_audiofile_views_are_disabled_by_default(self):
        self.reload()

        tests = [
            {
                'url': 'admin:media_albums_audiofile_changelist',
                'url_args': [],
            },
            {
                'url': 'admin:media_albums_audiofile_add',
                'url_args': [],
            },
            {
                'url': 'admin:media_albums_audiofile_change',
                'url_args': [1],
            },
            {
                'url': 'admin:media_albums_audiofile_delete',
                'url_args': [1],
            },
        ]

        for test in tests:
            self.assertRaises(
                NoReverseMatch,
                reverse,
                test['url'],
                args=test['url_args'],
            )

    @override_settings(MEDIA_ALBUMS={
        'audio_files_enabled': True,
    })
    def test_audiofile_views_audio_enabled(self):
        self.reload()

        tests = [
            {
                'url': 'admin:media_albums_audiofile_changelist',
                'url_args': [],
            },
            {
                'url': 'admin:media_albums_audiofile_add',
                'url_args': [],
            },
            {
                'url': 'admin:media_albums_audiofile_change',
                'url_args': [1],
            },
            {
                'url': 'admin:media_albums_audiofile_delete',
                'url_args': [1],
            },
        ]

        for test in tests:
            url = reverse(test['url'], args=test['url_args'])
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

            if test['url'][-4:] == '_add' or test['url'][-7:] == '_change':
                form = response.context['adminform'].form
                self.assertFalse(form.fields['audio_file_2'].required)

    @override_settings(MEDIA_ALBUMS={
        'audio_files_enabled': True,
        'audio_files_format2_required': True,
    })
    def test_audiofile_views_audio_enabled_with_format2_required(self):
        self.reload()

        tests = [
            {
                'url': 'admin:media_albums_audiofile_changelist',
                'url_args': [],
            },
            {
                'url': 'admin:media_albums_audiofile_add',
                'url_args': [],
            },
            {
                'url': 'admin:media_albums_audiofile_change',
                'url_args': [1],
            },
            {
                'url': 'admin:media_albums_audiofile_delete',
                'url_args': [1],
            },
        ]

        for test in tests:
            url = reverse(test['url'], args=test['url_args'])
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

            if test['url'][-4:] == '_add' or test['url'][-7:] == '_change':
                form = response.context['adminform'].form
                self.assertTrue(form.fields['audio_file_2'].required)

    def test_photo_views_are_enabled_by_default(self):
        self.reload()

        tests = [
            {
                'url': 'admin:media_albums_photo_changelist',
                'url_args': [],
            },
            {
                'url': 'admin:media_albums_photo_add',
                'url_args': [],
            },
            {
                'url': 'admin:media_albums_photo_change',
                'url_args': [1],
            },
            {
                'url': 'admin:media_albums_photo_delete',
                'url_args': [1],
            },
        ]

        for test in tests:
            url = reverse(test['url'], args=test['url_args'])
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    @override_settings(MEDIA_ALBUMS={
        'photos_enabled': False,
    })
    def test_photo_views_photos_disabled(self):
        self.reload()

        tests = [
            {
                'url': 'admin:media_albums_photo_changelist',
                'url_args': [],
            },
            {
                'url': 'admin:media_albums_photo_add',
                'url_args': [],
            },
            {
                'url': 'admin:media_albums_photo_change',
                'url_args': [1],
            },
            {
                'url': 'admin:media_albums_photo_delete',
                'url_args': [1],
            },
        ]

        for test in tests:
            self.assertRaises(
                NoReverseMatch,
                reverse,
                test['url'],
                args=test['url_args'],
            )

    def test_userphoto_views_are_disabled_by_default(self):
        self.reload()

        tests = [
            {
                'url': 'admin:media_albums_userphoto_changelist',
                'url_args': [],
            },
            {
                'url': 'admin:media_albums_userphoto_add',
                'url_args': [],
            },
            {
                'url': 'admin:media_albums_userphoto_change',
                'url_args': [1],
            },
            {
                'url': 'admin:media_albums_userphoto_delete',
                'url_args': [1],
            },
        ]

        for test in tests:
            self.assertRaises(
                NoReverseMatch,
                reverse,
                test['url'],
                args=test['url_args'],
            )

    @override_settings(MEDIA_ALBUMS={
        'user_uploaded_photos_enabled': True,
    })
    def test_userphoto_views_uploads_enabled(self):
        self.reload()

        tests = [
            {
                'url': 'admin:media_albums_userphoto_changelist',
                'url_args': [],
                'expected_status_code': 200,
            },
            {
                'url': 'admin:media_albums_userphoto_add',
                'url_args': [],
                'expected_status_code': 403,
            },
            {
                'url': 'admin:media_albums_userphoto_change',
                'url_args': [32],
                'expected_status_code': 200,
            },
            {
                'url': 'admin:media_albums_userphoto_delete',
                'url_args': [32],
                'expected_status_code': 200,
            },
        ]

        for test in tests:
            url = reverse(test['url'], args=test['url_args'])
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                test['expected_status_code']
            )

    @override_settings(MEDIA_ALBUMS={
        'user_uploaded_photos_enabled': True,
    })
    def test_userphoto_approval(self):
        self.reload()

        url = reverse('admin:media_albums_userphoto_changelist')
        user_photo_pk = 32
        album_kwargs = {
            'name': 'User Photos',
            'slug': 'user-photos',
        }

        self.assertEqual(UserPhoto.objects.filter(pk=user_photo_pk).count(), 1)
        self.assertEqual(Album.objects.filter(**album_kwargs).count(), 0)

        response = self.client.post(url, {
            'action': 'approve_photo',
            'select_across': '0',
            'index': '0',
            '_selected_action': str(user_photo_pk),
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(UserPhoto.objects.filter(pk=user_photo_pk).count(), 0)

        album = Album.objects.get(**album_kwargs)
        self.assertEqual(
            album.photo_set.filter(
                image='http://i.imgur.com/erJ6t2u.jpg',
            ).count(),
            1
        )

    @override_settings(MEDIA_ALBUMS={
        'user_uploaded_photos_enabled': True,
        'user_uploaded_photos_album_name': 'Photos Uploaded by Users',
        'user_uploaded_photos_album_slug': 'photos-from-users',
    })
    def test_userphoto_approval_with_custom_album_name_and_slug(self):
        self.reload()

        url = reverse('admin:media_albums_userphoto_changelist')
        user_photo_pk = 32
        album_kwargs = {
            'name': 'Photos Uploaded by Users',
            'slug': 'photos-from-users',
        }

        self.assertEqual(UserPhoto.objects.filter(pk=user_photo_pk).count(), 1)
        self.assertEqual(Album.objects.filter(**album_kwargs).count(), 0)

        response = self.client.post(url, {
            'action': 'approve_photo',
            'select_across': '0',
            'index': '0',
            '_selected_action': str(user_photo_pk),
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(UserPhoto.objects.filter(pk=user_photo_pk).count(), 0)

        album = Album.objects.get(**album_kwargs)
        self.assertEqual(
            album.photo_set.filter(
                image='http://i.imgur.com/erJ6t2u.jpg',
            ).count(),
            1
        )

    def test_videofile_views_are_disabled_by_default(self):
        self.reload()

        tests = [
            {
                'url': 'admin:media_albums_videofile_changelist',
                'url_args': [],
            },
            {
                'url': 'admin:media_albums_videofile_add',
                'url_args': [],
            },
            {
                'url': 'admin:media_albums_videofile_change',
                'url_args': [1],
            },
            {
                'url': 'admin:media_albums_videofile_delete',
                'url_args': [1],
            },
        ]

        for test in tests:
            self.assertRaises(
                NoReverseMatch,
                reverse,
                test['url'],
                args=test['url_args'],
            )

    @override_settings(MEDIA_ALBUMS={
        'video_files_enabled': True,
    })
    def test_videofile_views_video_enabled(self):
        self.reload()

        tests = [
            {
                'url': 'admin:media_albums_videofile_changelist',
                'url_args': [],
            },
            {
                'url': 'admin:media_albums_videofile_add',
                'url_args': [],
            },
            {
                'url': 'admin:media_albums_videofile_change',
                'url_args': [1],
            },
            {
                'url': 'admin:media_albums_videofile_delete',
                'url_args': [1],
            },
        ]

        for test in tests:
            url = reverse(test['url'], args=test['url_args'])
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

            if test['url'][-4:] == '_add' or test['url'][-7:] == '_change':
                form = response.context['adminform'].form
                self.assertFalse(form.fields['video_file_2'].required)

    @override_settings(MEDIA_ALBUMS={
        'video_files_enabled': True,
        'video_files_format2_required': True,
    })
    def test_videofile_views_video_enabled_with_format2_required(self):
        self.reload()

        tests = [
            {
                'url': 'admin:media_albums_videofile_changelist',
                'url_args': [],
            },
            {
                'url': 'admin:media_albums_videofile_add',
                'url_args': [],
            },
            {
                'url': 'admin:media_albums_videofile_change',
                'url_args': [1],
            },
            {
                'url': 'admin:media_albums_videofile_delete',
                'url_args': [1],
            },
        ]

        for test in tests:
            url = reverse(test['url'], args=test['url_args'])
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

            if test['url'][-4:] == '_add' or test['url'][-7:] == '_change':
                form = response.context['adminform'].form
                self.assertTrue(form.fields['video_file_2'].required)
