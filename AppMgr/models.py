from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from django.contrib.auth import get_user_model

from custom_user.models import AbstractEmailUser

from guardian.mixins import GuardianUserMixin

# Create your models here.
class UserProfile(AbstractEmailUser, GuardianUserMixin):

    public_contact = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("view_userprofile", "view profile information"),
        )

    def __unicode__(self):
        return self.email

class Organization(models.Model):
    name = models.CharField(max_length=255)

    members = models.ManyToManyField(UserProfile, through='Membership')

    class Meta:
        permissions = (
            ("view_organization", "view organization information"),
        )

    def __unicode__(self):
        return self.name

class Membership(models.Model):
    user = models.ForeignKey(UserProfile,  null=True, blank=False)
    org  = models.ForeignKey(Organization, null=True, blank=False)
    join_date = models.DateTimeField()
    
class Application(models.Model):
    name = models.CharField(max_length=255)

    isPublic = models.BooleanField(default=True)

    #Application owner can be either a UserProfile or an Organization    
    limit = models.Q(app_label='AppMgr', model='userprofile') | \
            models.Q(app_label='AppMgr', model='organization') 
    #limit = {'app_label__in': ('AppMgr',), 
    #         'model__in': ('UserProfile', 'Organization', ), }
    content_type = models.ForeignKey(
            ContentType,
            verbose_name='application owner',
            limit_choices_to=limit,
            null=True,
            blank=True,
    )
    object_id = models.PositiveIntegerField(
            verbose_name='app owner id',
            null=True,
    )
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        permissions = (
            ("view_application", "read access to the application"),
        )

    def __unicode__(self):
        return self.name

class AppVersion(models.Model):
    name = models.CharField(max_length=255)

    app = models.ForeignKey(Application, null=True, blank=False)

    aliases = JSONField()
    domain = models.URLField(max_length=255)

    def __unicode__(self):
        return self.name
