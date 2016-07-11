from collections import OrderedDict

try:
    from importlib import reload
except ImportError:
    pass

import os

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.urlresolvers import clear_url_caches, reverse
from django.test import TestCase
from django.test.utils import override_settings

from .. import admin as media_albums_admin
from ..settings import compute_settings
from . import urls as test_urls


class ViewsTest(TestCase):
    fixtures = [
        'media_albums_test_data.json',
    ]

    def get_user_types(self):
        for user_type, credentials in self.user_types.items():
            if credentials:
                self.client.login(**credentials)

            yield user_type

    def setUp(self):
        normal_credentials = {
            'username': 'normal_user',
            'password': 'testing!',
        }

        get_user_model()._default_manager.create_user(
            username=normal_credentials['username'],
            password=normal_credentials['password'],
            email='normal@example.com',
            first_name='Normal',
            last_name='User',
        )

        staff_credentials = {
            'username': 'staff_user',
            'password': 'testing!',
        }

        staff_user = get_user_model()._default_manager.create_user(
            username=staff_credentials['username'],
            password=staff_credentials['password'],
            email='staff@example.com',
            first_name='Staff',
            last_name='User',
        )

        staff_user.is_staff = True
        staff_user.save()

        self.user_types = OrderedDict([
            ('anonymous', None),
            ('normal', normal_credentials),
            ('staff', staff_credentials),
        ])

    def test_list_albums(self):
        compute_settings()
        url = reverse('list-albums')

        for user_type in self.get_user_types():
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

            # Make sure that:
            #
            # 1. Only the public albums are in the list
            # 2. The albums are in the expected order

            albums = response.context['object_list']
            self.assertEqual(len(albums), 5)
            self.assertEqual(albums[0].slug, 'cat-photos')
            self.assertEqual(albums[1].slug, 'dog-photos')
            self.assertEqual(albums[2].slug, 'empty-album')
            self.assertEqual(albums[3].slug, 'audio-files')
            self.assertEqual(albums[4].slug, 'video-files')

    @override_settings(MEDIA_ALBUMS={
        'paginate_by': 2,
    })
    def test_list_albums_pagination(self):
        compute_settings()
        url = reverse('list-albums')

        for user_type in self.get_user_types():
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

            # Make sure that:
            #
            # 1. Only the first two public albums are in the list
            # 2. The albums are in the expected order

            albums = response.context['object_list']
            self.assertEqual(len(albums), 2)
            self.assertEqual(albums[0].slug, 'cat-photos')
            self.assertEqual(albums[1].slug, 'dog-photos')

    def test_show_album(self):
        compute_settings()
        urls = {
            'public_album': reverse('show-album', kwargs={
                'album_slug': 'cat-photos',
            }),
            'unlisted_album': reverse('show-album', kwargs={
                'album_slug': 'funny-animated-gifs',
            }),
            'private_album': reverse('show-album', kwargs={
                'album_slug': 'miscellaneous',
            }),
        }

        for user_type in self.get_user_types():
            response = self.client.get(urls['public_album'])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context['items']), 10)

            response = self.client.get(urls['unlisted_album'])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context['items']), 5)

            response = self.client.get(urls['private_album'])

            if user_type == 'staff':
                expected_status_code = 200
            else:
                expected_status_code = 404

            self.assertEqual(response.status_code, expected_status_code)

            if expected_status_code == 200:
                items = response.context['items']
                self.assertEqual(len(items), 1)
                self.assertEqual(items[0].is_photo, True)

    @override_settings(MEDIA_ALBUMS={
        'audio_files_enabled': True,
    })
    def test_show_album_audio_enabled(self):
        compute_settings()
        url = reverse('show-album', kwargs={'album_slug': 'miscellaneous'})

        for user_type in self.get_user_types():
            response = self.client.get(url)

            if user_type == 'staff':
                expected_status_code = 200
            else:
                expected_status_code = 404

            self.assertEqual(response.status_code, expected_status_code)

            if expected_status_code == 200:
                items = response.context['items']
                self.assertEqual(len(items), 2)
                self.assertEqual(items[0].is_photo, True)
                self.assertEqual(items[1].is_audio, True)

    @override_settings(MEDIA_ALBUMS={
        'photos_enabled': False,
    })
    def test_show_album_photos_disabled(self):
        compute_settings()
        url = reverse('show-album', kwargs={'album_slug': 'miscellaneous'})

        for user_type in self.get_user_types():
            response = self.client.get(url)

            if user_type == 'staff':
                expected_status_code = 200
            else:
                expected_status_code = 404

            self.assertEqual(response.status_code, expected_status_code)

            if expected_status_code == 200:
                items = response.context['items']
                self.assertEqual(len(items), 0)

    @override_settings(MEDIA_ALBUMS={
        'video_files_enabled': True,
    })
    def test_show_album_video_enabled(self):
        compute_settings()
        url = reverse('show-album', kwargs={'album_slug': 'miscellaneous'})

        for user_type in self.get_user_types():
            response = self.client.get(url)

            if user_type == 'staff':
                expected_status_code = 200
            else:
                expected_status_code = 404

            self.assertEqual(response.status_code, expected_status_code)

            if expected_status_code == 200:
                items = response.context['items']
                self.assertEqual(len(items), 2)
                self.assertEqual(items[0].is_photo, True)
                self.assertEqual(items[1].is_video, True)

    @override_settings(MEDIA_ALBUMS={
        'audio_files_enabled': True,
        'video_files_enabled': True,
    })
    def test_show_album_audio_and_video_enabled(self):
        compute_settings()
        url = reverse('show-album', kwargs={'album_slug': 'miscellaneous'})

        for user_type in self.get_user_types():
            response = self.client.get(url)

            if user_type == 'staff':
                expected_status_code = 200
            else:
                expected_status_code = 404

            self.assertEqual(response.status_code, expected_status_code)

            if expected_status_code == 200:
                items = response.context['items']
                self.assertEqual(len(items), 3)
                self.assertEqual(items[0].is_photo, True)
                self.assertEqual(items[1].is_video, True)
                self.assertEqual(items[2].is_audio, True)

    @override_settings(MEDIA_ALBUMS={
        'audio_files_enabled': True,
        'video_files_enabled': True,
        'paginate_by': 2,
    })
    def test_show_album_audio_and_video_enabled_with_pagination(self):
        compute_settings()
        url = reverse('show-album', kwargs={'album_slug': 'miscellaneous'})

        for user_type in self.get_user_types():
            response = self.client.get(url)

            if user_type == 'staff':
                expected_status_code = 200
            else:
                expected_status_code = 404

            self.assertEqual(response.status_code, expected_status_code)

            if expected_status_code == 200:
                items = response.context['items']
                self.assertEqual(len(items), 2)
                self.assertEqual(items[0].is_photo, True)
                self.assertEqual(items[1].is_video, True)

    def test_show_audio(self):
        compute_settings()
        urls = {
            'public_album': reverse('show-audio', kwargs={
                'pk': 1,
            }),
            'private_album': reverse('show-audio', kwargs={
                'pk': 4,
            }),
        }

        for user_type in self.get_user_types():
            response = self.client.get(urls['public_album'])
            self.assertEqual(response.status_code, 404)

            response = self.client.get(urls['private_album'])
            self.assertEqual(response.status_code, 404)

    @override_settings(MEDIA_ALBUMS={
        'audio_files_enabled': True,
    })
    def test_show_audio_audio_enabled(self):
        compute_settings()
        urls = {
            'public_album': reverse('show-audio', kwargs={
                'pk': 1,
            }),
            'private_album': reverse('show-audio', kwargs={
                'pk': 4,
            }),
        }

        for user_type in self.get_user_types():
            response = self.client.get(urls['public_album'])
            self.assertEqual(response.status_code, 200)

            response = self.client.get(urls['private_album'])

            if user_type == 'staff':
                expected_status_code = 200
            else:
                expected_status_code = 404

            self.assertEqual(response.status_code, expected_status_code)

    def test_show_photo(self):
        compute_settings()
        urls = {
            'public_album': reverse('show-photo', kwargs={
                'pk': 1,
            }),
            'unlisted_album': reverse('show-photo', kwargs={
                'pk': 26,
            }),
            'private_album': reverse('show-photo', kwargs={
                'pk': 31,
            }),
        }

        for user_type in self.get_user_types():
            response = self.client.get(urls['public_album'])
            self.assertEqual(response.status_code, 200)

            response = self.client.get(urls['unlisted_album'])
            self.assertEqual(response.status_code, 200)

            response = self.client.get(urls['private_album'])

            if user_type == 'staff':
                expected_status_code = 200
            else:
                expected_status_code = 404

            self.assertEqual(response.status_code, expected_status_code)

    @override_settings(MEDIA_ALBUMS={
        'photos_enabled': False,
    })
    def test_show_photo_photos_disabled(self):
        compute_settings()
        urls = {
            'public_album': reverse('show-photo', kwargs={
                'pk': 1,
            }),
            'unlisted_album': reverse('show-photo', kwargs={
                'pk': 26,
            }),
            'private_album': reverse('show-photo', kwargs={
                'pk': 31,
            }),
        }

        for user_type in self.get_user_types():
            response = self.client.get(urls['public_album'])
            self.assertEqual(response.status_code, 404)

            response = self.client.get(urls['unlisted_album'])
            self.assertEqual(response.status_code, 404)

            response = self.client.get(urls['private_album'])
            self.assertEqual(response.status_code, 404)

    def test_show_video(self):
        compute_settings()
        urls = {
            'public_album': reverse('show-video', kwargs={
                'pk': 1,
            }),
            'private_album': reverse('show-video', kwargs={
                'pk': 4,
            }),
        }

        for user_type in self.get_user_types():
            response = self.client.get(urls['public_album'])
            self.assertEqual(response.status_code, 404)

            response = self.client.get(urls['private_album'])
            self.assertEqual(response.status_code, 404)

    @override_settings(MEDIA_ALBUMS={
        'video_files_enabled': True,
    })
    def test_show_video_video_enabled(self):
        compute_settings()
        urls = {
            'public_album': reverse('show-video', kwargs={
                'pk': 1,
            }),
            'private_album': reverse('show-video', kwargs={
                'pk': 4,
            }),
        }

        for user_type in self.get_user_types():
            response = self.client.get(urls['public_album'])
            self.assertEqual(response.status_code, 200)

            response = self.client.get(urls['private_album'])

            if user_type == 'staff':
                expected_status_code = 200
            else:
                expected_status_code = 404

            self.assertEqual(response.status_code, expected_status_code)

    def test_user_photo_upload(self):
        compute_settings()
        url = reverse('user-photo-upload')

        for user_type in self.get_user_types():
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)

    @override_settings(MEDIA_ALBUMS={
        'user_uploaded_photos_enabled': True,
    })
    def test_user_photo_upload_uploads_enabled(self):
        compute_settings()
        url = reverse('user-photo-upload')

        for user_type in self.get_user_types():
            response = self.client.get(url)

            if user_type == 'anonymous':
                expected_status_code = 302
            else:
                expected_status_code = 200

            self.assertEqual(response.status_code, expected_status_code)

            if expected_status_code == 302:
                self.assertIn(reverse('login'), response['Location'])

    @override_settings(MEDIA_ALBUMS={
        'user_uploaded_photos_enabled': True,
        'user_uploaded_photos_login_required': False,
    })
    def test_user_photo_upload_uploads_enabled_login_optional(self):
        compute_settings()
        url = reverse('user-photo-upload')

        for user_type in self.get_user_types():
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    @override_settings(MEDIA_ALBUMS={
        'user_uploaded_photos_enabled': True,
    })
    def test_user_photo_upload_uploads_enabled_post(self):
        compute_settings()
        reload(media_albums_admin)
        clear_url_caches()
        reload(test_urls)
        urls = {
            'form': reverse('user-photo-upload'),
            'success': reverse('user-photo-upload-success'),
        }

        tests_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'uploads',
        )

        for user_type in self.get_user_types():
            with open(
                os.path.join(tests_path, 'transparent.gif'),
                'rb'
            ) as upload:
                response = self.client.post(urls['form'], {
                    'name': 'Test',
                    'caption': 'Test caption',
                    'description': 'Test description',
                    'image': upload,
                })

            self.assertEqual(response.status_code, 302)

            if user_type == 'anonymous':
                self.assertIn(reverse('login'), response['Location'])
            else:
                self.assertIn(urls['success'], response['Location'])
                self.assertEqual(len(mail.outbox), 1)
                self.assertEqual(len(mail.outbox[0].to), 1)
                self.assertEqual(len(mail.outbox[0].cc), 0)
                self.assertEqual(len(mail.outbox[0].bcc), 0)
                self.assertEqual(
                    mail.outbox[0].to[0],
                    'dev@velocitywebworks.com'
                )
                mail.outbox = []

    def test_user_photo_upload_success(self):
        compute_settings()
        url = reverse('user-photo-upload-success')

        for user_type in self.get_user_types():
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)

    @override_settings(MEDIA_ALBUMS={
        'user_uploaded_photos_enabled': True,
    })
    def test_user_photo_upload_success_uploads_enabled(self):
        compute_settings()
        url = reverse('user-photo-upload-success')

        for user_type in self.get_user_types():
            response = self.client.get(url)

            if user_type == 'anonymous':
                expected_status_code = 302
            else:
                expected_status_code = 200

            self.assertEqual(response.status_code, expected_status_code)

            if expected_status_code == 302:
                self.assertIn(reverse('login'), response['Location'])

    @override_settings(MEDIA_ALBUMS={
        'user_uploaded_photos_enabled': True,
        'user_uploaded_photos_login_required': False,
    })
    def test_user_photo_upload_success_uploads_enabled_login_optional(self):
        compute_settings()
        url = reverse('user-photo-upload-success')

        for user_type in self.get_user_types():
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
