import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

BASE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'media_albums',
    'tests',
)

settings.configure(
    BASE_DIR=BASE_DIR,
    DEBUG=True,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'media_albums.sqlite3',
        }
    },
    ROOT_URLCONF='media_albums.tests.urls',
    INSTALLED_APPS=(
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.staticfiles',
        'bootstrap_pagination',
        'crispy_forms',
        'sorl.thumbnail',
        'media_albums',
    ),
    DEFAULT_FROM_EMAIL='dev@velocitywebworks.com',
    MIDDLEWARE_CLASSES=(
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django.middleware.security.SecurityMiddleware',
    ),
    MEDIA_ROOT=os.path.join(BASE_DIR, 'media'),
    MEDIA_URL='/media/',
    STATIC_ROOT=os.path.join(BASE_DIR, 'static'),
    STATIC_URL='/static/',
    TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(BASE_DIR, 'templates')],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ],
    CRISPY_TEMPLATE_PACK='bootstrap3',
    FIXTURE_DIRS=[os.path.join(BASE_DIR, 'fixtures')],
)


def runtests():
    django.setup()
    apps = sys.argv[1:] or ['media_albums', ]
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True, failfast=False)
    failures = test_runner.run_tests(apps)
    sys.exit(failures)


if __name__ == '__main__':
    runtests()
