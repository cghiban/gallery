from django.core.management.base import BaseCommand

from photos.models import Photo, Thumbnail


class Command(BaseCommand):
    help = 'Deletes photos and thumbnails from the filesystem that no ' \
           'longer exist in the database.'

    def handle(self, *args, **options):
        """
        Removes all photos that do not exist for Photos and for Thumbnails.
        """
        verbosity = int(options['verbosity'])
        self.cleanup_files(Photo, 'file', 'photos/photo', verbosity)
        self.cleanup_files(Thumbnail, 'file', 'photos/thumbnail', verbosity)
        self.stdout.write('Successfully cleaned up.')

    def cleanup_files(self, model_class, field, dirname, verbosity):
        """
        Removes all files on the file storage that do not exist in the given
        model_class and field anymore. This assumes that the only things in the
        given dirname are files that belong to the given model_class and field.
        If that assumption is not correct then do not use this method or you
        will permanently lose data!
        """
        storage = model_class._meta.get_field(field).storage
        model_files = self.get_model_files(model_class, field)
        storage_files = self.get_storage_files(storage, dirname)
        files_to_delete = set(storage_files) - set(model_files)
        data = {
            'count': len(files_to_delete),
            'model': model_class._meta.model_name,
            'field': field
        }
        self.stdout.write(
            'Deleting {count} files from {model}.{field}...'.format(**data))
        self.delete_files(storage, files_to_delete, verbosity)

    def delete_files(self, storage, file_list, verbosity):
        """
        Deletes all files in file_list using storage. There's no turning back
        from this, so be sure that you want to delete all these files.
        """
        for filename in file_list:
            if verbosity > 1:
                self.stdout.write(filename)
            storage.delete(filename)

    def get_model_files(self, model_class, field):
        """
        Return a generator containing all the filenames in the given
        model_class and field.
        """
        for filename in model_class.objects.values_list(field, flat=True):
            yield filename

    def get_storage_files(self, storage, dirname):
        """
        Return a generator containing all the filenames in the given dirname
        using the given storage instance.
        """
        try:
            directories, files = storage.listdir(dirname)
        except FileNotFoundError:
            return []
        for filename in files:
            yield '{}/{}'.format(dirname, filename)
