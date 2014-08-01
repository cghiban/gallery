from django.db.models import FileField


def delete_files_on_delete(sender, instance, **kwargs):
    """
    Deletes files from filesystem when corresponding instance object is
    deleted.
    """
    for field in instance._meta.fields:
        if not isinstance(field, FileField):
            continue
        file_field = getattr(instance, field.name)
        storage = file_field.storage
        if file_field and storage and storage.exists(file_field.name):
            storage.delete(file_field.name)


def delete_files_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem when a file is changed on an instance.
    """
    if not instance.pk:
        return

    try:
        old_instance = instance.__class__.objects.get(pk=instance.pk)
    except instance.DoesNotExist:
        return

    for field in instance._meta.fields:
        if not isinstance(field, FileField):
            continue
        old_file = getattr(old_instance, field.name)
        new_file = getattr(instance, field.name)
        storage = old_file.storage
        if old_file != new_file and storage and storage.exists(old_file.name):
            storage.delete(old_file.name)
