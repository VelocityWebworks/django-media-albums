from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered, NotRegistered
from django.template.defaultfilters import linebreaksbr
from django.utils.translation import ugettext_lazy as _

from .forms import AudioFileForm, PhotoForm, VideoFileForm
from .models import AudioFile, Album, Photo, UserPhoto, VideoFile
from .settings import MEDIA_ALBUMS_SETTINGS


class AudioFileInline(admin.StackedInline):
    model = AudioFile
    form = AudioFileForm

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.audiofile_set.exists():
            return 0
        return 1


class PhotoInline(admin.StackedInline):
    model = Photo
    form = PhotoForm

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.photo_set.exists():
            return 0
        return 1


class VideoFileInline(admin.StackedInline):
    model = VideoFile
    form = VideoFileForm

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.videofile_set.exists():
            return 0
        return 1


class AlbumAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'num_items', 'ordering', 'created', 'visibility')
    prepopulated_fields = {'slug': ('name',)}
    save_on_top = True

    def __init__(self, *args, **kwargs):
        super(AlbumAdmin, self).__init__(*args, **kwargs)

        inlines = []

        if MEDIA_ALBUMS_SETTINGS['photos_enabled']:
            inlines.append(PhotoInline)

        if MEDIA_ALBUMS_SETTINGS['video_files_enabled']:
            inlines.append(VideoFileInline)

        if MEDIA_ALBUMS_SETTINGS['audio_files_enabled']:
            inlines.append(AudioFileInline)

        self.inlines = inlines


class AudioFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'album', 'ordering', 'created')
    list_filter = ('album',)
    ordering = ('album__ordering', 'album__name', 'ordering', 'name')
    form = AudioFileForm


class PhotoAdmin(admin.ModelAdmin):
    list_display = ('name', 'album', 'ordering', 'created')
    list_filter = ('album',)
    ordering = ('album__ordering', 'album__name', 'ordering', 'name')
    form = PhotoForm


class UserPhotoAdmin(admin.ModelAdmin):
    actions = ['approve_photo']
    list_display = (
        'name',
        'image_link',
        'added_by',
        'caption',
        'description_formatted',
        'ordering',
        'created',
    )
    readonly_fields = (
        'album',
        'image',
        'added_by',
    )

    def approve_photo(modeladmin, request, queryset):
        for obj in queryset:
            obj.approve()
    approve_photo.short_description = _('Approve Photos')

    def has_add_permission(self, request):
        return False

    def description_formatted(self, obj):
        return linebreaksbr(obj.description)
    description_formatted.admin_order_field = 'description'
    description_formatted.short_description = _('description')

    def image_link(self, obj):
        return '<a href="%s" target="_blank">Preview </a>' % obj.image.url
    image_link.allow_tags = True
    image_link.short_description = _('view photo')


class VideoFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'album', 'ordering', 'created')
    list_filter = ('album',)
    ordering = ('album__ordering', 'album__name', 'ordering', 'name')
    form = VideoFileForm

try:
    admin.site.register(Album, AlbumAdmin)
except AlreadyRegistered:
    pass

if MEDIA_ALBUMS_SETTINGS['audio_files_enabled']:
    try:
        admin.site.register(AudioFile, AudioFileAdmin)
    except AlreadyRegistered:
        pass
else:
    try:
        admin.site.unregister(AudioFile)
    except NotRegistered:
        pass

if MEDIA_ALBUMS_SETTINGS['photos_enabled']:
    try:
        admin.site.register(Photo, PhotoAdmin)
    except AlreadyRegistered:
        pass
else:
    try:
        admin.site.unregister(Photo)
    except NotRegistered:
        pass

if MEDIA_ALBUMS_SETTINGS['user_uploaded_photos_enabled']:
    try:
        admin.site.register(UserPhoto, UserPhotoAdmin)
    except AlreadyRegistered:
        pass
else:
    try:
        admin.site.unregister(UserPhoto)
    except NotRegistered:
        pass

if MEDIA_ALBUMS_SETTINGS['video_files_enabled']:
    try:
        admin.site.register(VideoFile, VideoFileAdmin)
    except AlreadyRegistered:
        pass
else:
    try:
        admin.site.unregister(VideoFile)
    except NotRegistered:
        pass
