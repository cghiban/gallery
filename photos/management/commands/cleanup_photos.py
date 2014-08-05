import os

from django.core.management.base import BaseCommand
from django.conf import settings

from photos.models import Photo, Thumbnail


class Command(BaseCommand):
    help = 'Deletes photos and thumbnails from the filesystem that no ' \
           'longer exist in the database.'

    def handle(self, *args, **options):
        verbosity = options['verbosity']
        self.cleanup_model_files(Photo, 'file', 'photos', verbosity=verbosity)
        self.cleanup_model_files(Thumbnail, 'file', 'photos/thumbnails',
                                 verbosity=verbosity)
        self.stdout.write('Successfully cleaned up.')

    def cleanup_model_files(self, model_class, field, dir, verbosity):
        model_files = self.get_model_files(model_class, field)
        filesystem_files = self.get_filesystem_files(dir)
        file_list = set(filesystem_files) - set(model_files)
        data = {'count': len(file_list), 'model': model_class._meta.model_name}
        self.stdout.write('Deleting {count} {model} files...'.format(**data))
        self.delete_files(file_list, verbosity)

    def delete_files(self, file_list, verbosity):
        for filename in file_list:
            if verbosity > 1:
                self.stdout.write(filename)
            os.remove(filename)

    def get_model_files(self, model_class, field):
        for filename in model_class.objects.values_list(field, flat=True):
            yield os.path.join(settings.MEDIA_ROOT, filename)

    def get_filesystem_files(self, dir):
        media_root = settings.MEDIA_ROOT
        full_dir = os.path.join(media_root, dir)
        for filename in os.listdir(full_dir):
            full_path = os.path.join(full_dir, filename)
            if not os.path.isfile(full_path):
                continue
            yield full_path
