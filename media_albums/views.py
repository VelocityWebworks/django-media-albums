from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, FormView, ListView, TemplateView

from .models import Album, AudioFile, Photo, VideoFile
from .forms import UserPhotoForm
from .settings import MEDIA_ALBUMS_SETTINGS


class AlbumItemDetailView(DetailView):
    item_type = None
    template_name = 'media_albums/album_item_detail.html'

    def dispatch(self, request, *args, **kwargs):
        if self.item_type == 'photo':
            self.model = Photo
            settings_key = 'photos_enabled'
        elif self.item_type == 'video':
            self.model = VideoFile
            settings_key = 'video_files_enabled'
        elif self.item_type == 'audio':
            self.model = AudioFile
            settings_key = 'audio_files_enabled'

        if MEDIA_ALBUMS_SETTINGS[settings_key]:
            return super(AlbumItemDetailView, self).dispatch(
                request,
                *args,
                **kwargs
            )

        raise Http404

    def get_queryset(self):
        qs = self.model.objects.select_related('album').all()

        if not self.request.user.is_staff:
            qs = qs.exclude(
                album__visibility=Album.VISIBILITY_PRIVATE,
            )

        return qs


class AlbumListView(ListView):
    queryset = Album.objects.filter(
        visibility=Album.VISIBILITY_PUBLIC,
    )

    def get_paginate_by(self, queryset):
        return MEDIA_ALBUMS_SETTINGS['paginate_by']


class UserPhotoUploadView(FormView):
    form_class = UserPhotoForm
    success_url = reverse_lazy('user-photo-upload-success')
    template_name = 'media_albums/upload.html'

    def dispatch(self, request, *args, **kwargs):
        if not MEDIA_ALBUMS_SETTINGS['user_uploaded_photos_enabled']:
            raise Http404

        if MEDIA_ALBUMS_SETTINGS['user_uploaded_photos_login_required']:
            return self.dispatch_login_required(
                request,
                *args,
                **kwargs
            )

        return super(UserPhotoUploadView, self).dispatch(
            request,
            *args,
            **kwargs
        )

    @method_decorator(login_required)
    def dispatch_login_required(self, request, *args, **kwargs):
        return super(UserPhotoUploadView, self).dispatch(
            request,
            *args,
            **kwargs
        )

    def form_valid(self, form):
        u_photo = form.save(commit=False)

        if self.request.user.is_authenticated():
            u_photo.added_by = self.request.user

        u_photo.album = Album.objects.get_or_create(
            name='User Uploaded Photos Pending Approval',
            slug='user-uploaded-photos-pending-approval',
            visibility=Album.VISIBILITY_PRIVATE,
            ordering=999,
        )[0]

        u_photo.save()

        email_subject_context = {}

        email_subject = render_to_string(
            'media_albums/emails/user_photo_uploaded-subject.txt',
            email_subject_context,
        ).strip()

        email_body_context = {
            'admin_url': self.request.build_absolute_uri(
                reverse('admin:media_albums_userphoto_changelist')
            ),
        }

        email_body_text = render_to_string(
            'media_albums/emails/user_photo_uploaded.txt',
            email_body_context,
        )

        send_mail(
            email_subject,
            email_body_text,
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
        )

        return HttpResponseRedirect(self.get_success_url())


class UserPhotoUploadSuccessView(TemplateView):
    template_name = 'media_albums/upload-success.html'

    def dispatch(self, request, *args, **kwargs):
        if not MEDIA_ALBUMS_SETTINGS['user_uploaded_photos_enabled']:
            raise Http404

        if MEDIA_ALBUMS_SETTINGS['user_uploaded_photos_login_required']:
            return self.dispatch_login_required(
                request,
                *args,
                **kwargs
            )

        return super(UserPhotoUploadSuccessView, self).dispatch(
            request,
            *args,
            **kwargs
        )

    @method_decorator(login_required)
    def dispatch_login_required(self, request, *args, **kwargs):
        return super(UserPhotoUploadSuccessView, self).dispatch(
            request,
            *args,
            **kwargs
        )


def show_album(
    request, album_slug, template_name='media_albums/album_detail.html'
):
    album = Album.objects.filter(
        slug=album_slug,
    )

    if not request.user.is_staff:
        album = album.exclude(
            visibility=Album.VISIBILITY_PRIVATE,
        )

    try:
        album = album.get()
    except Album.DoesNotExist:
        raise Http404

    media_albums_objs = []

    if MEDIA_ALBUMS_SETTINGS['photos_enabled']:
        media_albums_objs.extend(
            Photo.objects.filter(album=album).order_by('ordering', 'name')
        )

    if MEDIA_ALBUMS_SETTINGS['video_files_enabled']:
        media_albums_objs.extend(
            VideoFile.objects.filter(album=album).order_by('ordering', 'name')
        )

    if MEDIA_ALBUMS_SETTINGS['audio_files_enabled']:
        media_albums_objs.extend(
            AudioFile.objects.filter(album=album).order_by('ordering', 'name')
        )

    paginator = Paginator(
        media_albums_objs,
        MEDIA_ALBUMS_SETTINGS['paginate_by'],
        allow_empty_first_page=True
    )

    page = request.GET.get('page') or 1

    try:
        page_number = int(page)
    except ValueError:
        raise Http404

    try:
        items = paginator.page(page_number)
    except InvalidPage:
        raise Http404

    context_data = {
        'album': album,
        'items': items.object_list,
        'is_paginated': paginator.num_pages > 1,
        'page': items.number,
        'page_obj': items,
        'has_next': items.has_next(),
        'has_previous': items.has_previous(),
        'pages': paginator.num_pages,
        'page_range': paginator.page_range,
        'paginator': paginator,
    }

    if items.has_next():
        context_data['next'] = items.next_page_number()

    if items.has_previous():
        context_data['previous'] = items.previous_page_number()

    return render_to_response(
        template_name,
        context_data,
        context_instance=RequestContext(request),
    )
