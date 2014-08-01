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
        if file_field.path:
            storage.delete(file_field.path)


def delete_files_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem when a file is changed on an instance.
    """
    if not instance.pk:
        return False

    try:
        old_instance = instance.__class__.objects.get(pk=instance.pk)
    except instance.__class__.DoesNotExist:
        return False

    for field in instance._meta.fields:
        if not isinstance(field, FileField):
            continue
        old_file_field = getattr(old_instance, field.name)
        new_file_field = getattr(instance, field.name)
        if old_file_field.path and old_file_field.name != new_file_field.name:
            old_file_field.storage.delete(old_file_field.path)
