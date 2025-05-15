# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]
### Added
- Added the ability to allow for multiple audio or video formats.

## [0.1.3] - 2016-11-17
### Fixed
- Previously, albums with multiple media types would always have photos first,
  then video files, and then audio files, regardless of the values of the
  `ordering` and `name` columns. Now it is possible for the media types to
  appear in any order.
- Added the `on_delete` argument to the foreign keys to fix a Django 1.10
  warning. For more information, see
  [the "ForeignKey and OneToOneField on_delete argument" section](https://docs.djangoproject.com/en/dev/releases/1.9/#foreignkey-and-onetoonefield-on-delete-argument)
  of the Django 1.9 release notes.

## [0.1.2] - 2016-08-01
### Fixed
- This app now works with Django 1.10.

## [0.1.1] - 2016-07-11
### Fixed
- Fixed some bugs with EXIF orientation handling.
- Fixed tests.
