from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone


class Action(models.Model):
    """
    An action is something that a user did.
    Nomenclature mostly based on http://activitystrea.ms/specs/atom/1.0/

    Generalized Format:
        <user> <verb>
        <user> <verb> <target>
        <user> <verb> <action_object> <target>
        <user> <verb> <action_object> <join> <target>

    Examples:
        <tim> <added new photos>
        <tim> <added 5 photos to the album> <Album Name>
        <tim> <tagged> <Photo Name> <Album Name>
        <tim> <tagged> <john> <in the album> <Album Name>
    """

    timestamp = models.DateTimeField(_('timestamp'), default=timezone.now)
    verb = models.CharField(_('verb'), max_length=200)
    join = models.CharField(_('join'), max_length=50, null=True, blank=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'))

    target_content_type = models.ForeignKey(
        ContentType, related_name='target', blank=True, null=True)
    target_object_id = models.CharField(max_length=200, blank=True, null=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    action_object_content_type = models.ForeignKey(
        ContentType, related_name='action_object', blank=True, null=True)
    action_object_object_id = models.CharField(
        max_length=200, blank=True, null=True)
    action_object = GenericForeignKey(
        'action_object_content_type', 'action_object_object_id')

    class Meta:
        verbose_name = _('action')
        verbose_name_plural = _('actions')
        ordering = ['-timestamp', ]

    def __str__(self):
        ctx = {
            'actor': self.user.get_full_name() or self.user.username,
            'verb': self.verb,
            'join': self.join,
            'object': self.action_object,
            'target': self.target
        }
        if self.target:
            if self.action_object:
                return '{actor} {verb} {object} {join} {target}'.format(**ctx)
            return '{actor} {verb} {target}'.format(**ctx)
        if self.action_object:
            return '{actor} {verb} {object}'.format(**ctx)
        return '{actor} {verb}'.format(**ctx)


def delete_actions_on_delete(sender, **kwargs):
    """
    This signal attempts to delete any activity which is related to Action
    through a generic relation.
    """
    content_type = ContentType.objects.get_for_model(kwargs['instance'])
    instance_pk = kwargs['instance'].pk

    Action.objects.filter(
        action_object_object_id=instance_pk,
        action_object_content_type=content_type
    ).delete()

    Action.objects.filter(
        target_object_id=instance_pk,
        target_content_type=content_type
    ).delete()


models.signals.pre_delete.connect(delete_actions_on_delete)
