from itertools import chain

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import NoReverseMatch, reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from PIL import Image

from .settings import MEDIA_ALBUMS_SETTINGS


class Upload(models.Model):
    album = models.ForeignKey('Album')
    name = models.CharField(_('name'), max_length=200)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    ordering = models.IntegerField(
        _('ordering'),
        default=0,
        help_text=_('Override automatic ordering.'),
        db_index=True,
    )

    is_audio = False
    is_photo = False
    is_video = False

    class Meta:
        abstract = True
        ordering = ('ordering', 'name')

    def save(self, *args, **kwargs):
        # All of the models that inherit from this abstract base class
        # have an `album_photo` field.

        if self.album_photo:
            AudioFile.objects.filter(
                album=self.album,
                album_photo=True,
            ).update(
                album_photo=False,
            )

            Photo.objects.filter(
                album=self.album,
                album_photo=True,
            ).update(
                album_photo=False,
            )

            VideoFile.objects.filter(
                album=self.album,
                album_photo=True,
            ).update(
                album_photo=False,
            )
        super(Upload, self).save(*args, **kwargs)


class Album(models.Model):
    VISIBILITY_PUBLIC = 'public'
    VISIBILITY_UNLISTED = 'unlisted'
    VISIBILITY_PRIVATE = 'private'
    VISIBILITY_CHOICES = (
        (
            VISIBILITY_PUBLIC,
            _('Public')
        ),
        (
            VISIBILITY_UNLISTED,
            _(
                'Unlisted - this album will not be shown in the list of '
                'albums, but anybody who has the URL will be able to view it'
            )
        ),
        (
            VISIBILITY_PRIVATE,
            _(
                'Private - this album will not be shown in the list of '
                'albums, but staff users will be able to view it'
            )
        ),
    )

    name = models.CharField(_('name'), max_length=200, unique=True)
    slug = models.SlugField(_('slug'), unique=True)
    description = models.TextField(_('description'), blank=True)
    visibility = models.CharField(
        _('visibility'),
        choices=VISIBILITY_CHOICES,
        max_length=8,
    )
    created = models.DateTimeField(_('created'), auto_now_add=True)
    ordering = models.IntegerField(
        _('ordering'),
        default=0,
        help_text=_('Override automatic ordering.'),
    )

    class Meta:
        ordering = ('ordering', 'name')
        verbose_name = _('album')
        verbose_name_plural = _('albums')

    def __unicode__(self):
        return self.name

    def cover_item(self):
        cover_item = None

        if MEDIA_ALBUMS_SETTINGS['photos_enabled']:
            try:
                cover_item = self.photo_set.filter(
                    album_photo=True,
                )[0]
            except IndexError:
                pass

        if cover_item is None and MEDIA_ALBUMS_SETTINGS['video_files_enabled']:
            try:
                cover_item = self.videofile_set.filter(
                    album_photo=True,
                )[0]
            except IndexError:
                pass

        if cover_item is None and MEDIA_ALBUMS_SETTINGS['audio_files_enabled']:
            try:
                cover_item = self.audiofile_set.filter(
                    album_photo=True,
                )[0]
            except IndexError:
                pass

        return cover_item

    def image(self):
        cover_item = self.cover_item()

        if cover_item:
            if cover_item.is_photo:
                return cover_item.image
            elif cover_item.is_video:
                return cover_item.poster
            elif cover_item.is_audio:
                return cover_item.cover_art

        return None

    def num_items(self):
        """
        Return the number of photos associated with this album
        """
        return len(self.items)
    num_items.short_description = _('Items')

    @property
    def items(self):
        querysets = []

        if MEDIA_ALBUMS_SETTINGS['photos_enabled']:
            querysets.append(self.photo_set.all())

        if MEDIA_ALBUMS_SETTINGS['video_files_enabled']:
            querysets.append(self.videofile_set.all())

        if MEDIA_ALBUMS_SETTINGS['audio_files_enabled']:
            querysets.append(self.audiofile_set.all())

        return list(chain(*querysets))


class AudioFile(Upload):
    is_audio = True

    caption = models.CharField(
        _('caption'),
        max_length=255,
        blank=True,
        help_text=_('A brief caption describing the audio.'),
    )
    description = models.TextField(
        _('description'),
        help_text=_('A more in-depth description of the audio.'),
        blank=True,
    )
    audio_file_1 = models.FileField(
        _('audio file 1'),
        upload_to='media_albums/%Y/%m/%d/audio',
        help_text=(
            _('Use this field to upload the audio in %s format.') %
            MEDIA_ALBUMS_SETTINGS['audio_files_format1_extension'].lower()
        ),
    )
    audio_file_2 = models.FileField(
        _('audio file 2'),
        upload_to='media_albums/%Y/%m/%d/audio',
        help_text=(
            _(
                'Use this field to upload the same audio in %s format. Having '
                'the same audio in a second format will allow more web '
                'browsers to be able to play the audio file.'
            ) % MEDIA_ALBUMS_SETTINGS['audio_files_format2_extension'].lower()
        ),
        blank=True,
    )
    cover_art = models.ImageField(
        _('cover art'),
        upload_to='media_albums/%Y/%m/%d/audio',
        help_text=_('The image to display below the audio player.'),
        blank=True,
    )
    album_photo = models.BooleanField(
        _('album photo'),
        default=False,
        help_text=_('Use the cover art as the album photo.'),
    )

    class Meta(Upload.Meta):
        verbose_name = _('audio file')
        verbose_name_plural = _('audio files')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        try:
            url = reverse('show-audio', args=[self.id])
        except NoReverseMatch:
            url = self.audio_file_1.url

        return url

    def clean(self):
        errors = {}

        for i in (1, 2):
            value = getattr(self, 'audio_file_%s' % i)

            if value:
                actual_ext = value.name.rsplit('.', 1)[-1].lower()
                expected_ext = MEDIA_ALBUMS_SETTINGS[
                    'audio_files_format%s_extension' % i
                ].lower()

                if actual_ext != expected_ext:
                    errors['audio_file_%s' % i] = _(
                        'The file you uploaded appears to be in %s format. It '
                        'needs to be in %s format.'
                    ) % (actual_ext, expected_ext)

        if self.album_photo and not self.cover_art:
            errors['album_photo'] = _(
                'You cannot have this checkbox checked unless the audio has '
                'cover art.'
            )

        if errors:
            raise ValidationError(errors)


class Photo(Upload):
    is_photo = True

    caption = models.CharField(
        _('caption'),
        max_length=255,
        blank=True,
        help_text=_('A brief caption describing the photo.'),
    )
    description = models.TextField(
        _('description'),
        help_text=_('A more in-depth description of the photo.'),
        blank=True,
    )
    image = models.ImageField(
        _('image'),
        upload_to='media_albums/%Y/%m/%d/photo',
    )
    album_photo = models.BooleanField(
        _('album photo'),
        default=False,
        help_text=_('Use this photo as the album photo.'),
    )

    class Meta(Upload.Meta):
        verbose_name = _('photo')
        verbose_name_plural = _('photos')

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Photo, self).save(*args, **kwargs)

        exif_data = None

        try:
            img = Image.open(self.image)
        except IOError:
            pass
        else:
            try:
                exif_data = img._getexif()
            except AttributeError:
                pass

        if exif_data:
            orientation = exif_data.get(0x0112)

            rotated_img = None

            if orientation == 2:
                rotated_img = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 3:
                rotated_img = img.rotate(180)
            elif orientation == 4:
                rotated_img = img.transpose(Image.FLIP_TOP_BOTTOM)
            elif orientation == 5:
                rotated_img = img.rotate(-90).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 6:
                rotated_img = img.rotate(-90)
            elif orientation == 7:
                rotated_img = img.rotate(90).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 8:
                rotated_img = img.rotate(90)

            if rotated_img:
                try:
                    rotated_img.save(self.image.file.name, overwrite=True)
                except IOError:
                    pass

    def get_absolute_url(self):
        try:
            url = reverse('show-photo', args=[self.id])
        except NoReverseMatch:
            url = self.image.url

        return url


class UserPhoto(Photo):
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
    )

    def approve(self):
        p = Photo()
        for attr, val in self.__dict__.items():
            if attr[0] != '_' and attr != 'id' and hasattr(p, attr):
                setattr(p, attr, val)
        p.album = Album.objects.get_or_create(
            name=MEDIA_ALBUMS_SETTINGS['user_uploaded_photos_album_name'],
            defaults={
                'slug': MEDIA_ALBUMS_SETTINGS[
                    'user_uploaded_photos_album_slug'
                ],
                'visibility': Album.VISIBILITY_PUBLIC,
            },
        )[0]
        p.save()
        self.delete()
        return p


class VideoFile(Upload):
    is_video = True

    caption = models.CharField(
        _('caption'),
        max_length=255,
        blank=True,
        help_text=_('A brief caption describing the video.'),
    )
    description = models.TextField(
        _('description'),
        help_text='A more in-depth description of the video.',
        blank=True,
    )
    video_file_1 = models.FileField(
        _('video file 1'),
        upload_to='media_albums/%Y/%m/%d/video',
        help_text=(
            _('Use this field to upload the video in %s format.') %
            MEDIA_ALBUMS_SETTINGS['video_files_format1_extension'].lower()
        ),
    )
    video_file_2 = models.FileField(
        _('video file 2'),
        upload_to='media_albums/%Y/%m/%d/video',
        help_text=(
            _(
                'Use this field to upload the same video in %s format. Having '
                'the same video in a second format will allow more web '
                'browsers to be able to play the video file.'
            ) % MEDIA_ALBUMS_SETTINGS['video_files_format2_extension'].lower()
        ),
        blank=True,
    )
    poster = models.ImageField(
        _('poster'),
        upload_to='media_albums/%Y/%m/%d/video',
        help_text=_(
            'The image to use for the poster frame (the poster frame is what '
            'shows until the user plays or seeks). If you leave this blank, '
            'nothing is displayed until the video\'s first frame is '
            'available; then the first frame is shown as the poster frame.'
        ),
        blank=True,
    )
    album_photo = models.BooleanField(
        _('album photo'),
        default=False,
        help_text=_('Use the poster as the album photo.'),
    )

    class Meta(Upload.Meta):
        verbose_name = _('video file')
        verbose_name_plural = _('video files')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        try:
            url = reverse('show-video', args=[self.id])
        except NoReverseMatch:
            url = self.video_file_1.url

        return url

    def clean(self):
        errors = {}

        for i in (1, 2):
            value = getattr(self, 'video_file_%s' % i)

            if value:
                actual_ext = value.name.rsplit('.', 1)[-1].lower()
                expected_ext = MEDIA_ALBUMS_SETTINGS[
                    'video_files_format%s_extension' % i
                ].lower()

                if actual_ext != expected_ext:
                    errors['video_file_%s' % i] = _(
                        'The file you uploaded appears to be in %s format. It '
                        'needs to be in %s format.'
                    ) % (actual_ext, expected_ext)

        if self.album_photo and not self.poster:
            errors['album_photo'] = _(
                'You cannot have this checkbox checked unless the video has a '
                'poster.'
            )

        if errors:
            raise ValidationError(errors)
