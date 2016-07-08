from django.conf.urls import url

from .views import (
    AlbumItemDetailView, AlbumListView, UserPhotoUploadView,
    UserPhotoUploadSuccessView, show_album
)

urlpatterns = [
    url(r'^$', AlbumListView.as_view(), name='list-albums'),
    url(
        r'^audio/(?P<pk>\d+)/$',
        AlbumItemDetailView.as_view(item_type='audio'),
        name='show-audio',
    ),
    url(
        r'^photo/(?P<pk>\d+)/$',
        AlbumItemDetailView.as_view(item_type='photo'),
        name='show-photo',
    ),
    url(
        r'^add/$',
        UserPhotoUploadView.as_view(),
        name='user-photo-upload',
    ),
    url(
        r'^add/success/$',
        UserPhotoUploadSuccessView.as_view(),
        name='user-photo-upload-success',
    ),
    url(
        r'^video/(?P<pk>\d+)/$',
        AlbumItemDetailView.as_view(item_type='video'),
        name='show-video',
    ),
    url(
        r'^(?P<album_slug>[-\w]+)/$',
        show_album,
        name='show-album',
    ),
]
