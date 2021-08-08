import binascii
from datetime import datetime, date
from time import mktime


from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from mongoengine import Document, ImproperlyConfigured, fields
from mongoengine.django import auth

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import (
    _user_get_all_permissions,
    _user_has_module_perms,
    _user_has_perm,
)

from messages.models import Messagebox

class User(Document):
    ROLE_CHOICES=(
        ("u","user"),
        ("e","editor"),
    )

    id = fields.SequenceField(primary_key=True)
    phone_number = fields.StringField(max_length=11,unique=True, required=True)
    password = fields.StringField(
        max_length=128,
        verbose_name=_("password"),
        help_text=_(
            "Use '[algo]$[iterfollowed_boleanations]$[salt]$[hexdigest]' or use the <a href=\"password/\">change password form</a>."
        ),
    )
    username = fields.StringField(max_length=200,unique=True,required=True)
    name = fields.StringField(max_length=50, default='')
    email = fields.EmailField()
    lastname = fields.StringField(max_length=50, default='')
    biography = fields.StringField()

    is_staff = fields.BooleanField(default=False)
    is_superuser = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=True)

    joined_date = fields.FloatField(default=0)

    role = fields.StringField(choices=ROLE_CHOICES,default="u")

    followings = fields.ListField(fields.ReferenceField("User"))
    followers = fields.ListField(fields.ReferenceField("User"))

    followings_cnt = fields.IntField(default=0)
    followers_cnt = fields.IntField(default=0)

    #Watchlist

    watchlist = fields.ListField(fields.StringField())

    #plan user

    plan = fields.ReferenceField("Plan", null=True)

    #device token for andrioid users
    device_token = fields.StringField()

    avatar = fields.ReferenceField("Image", null=True)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []



    #functions -> password

    def __str__(self):
        return self.mobile_number

    def get_short_name(self):
        return self.mobile_number

    def get_full_name(self):
        return self.mobile_number

    def __unicode__(self):
        return self.mobile_number

    def set_password(self, raw_password):
        """
        Sets the user's password - always use this rather than directly
        assigning to :attr:`~mongoengine.django.auth.User.password` as the
        password is hashed before storage.
        """
        self.password = make_password(raw_password)
        self.save()
        return self

    def check_password(self, raw_password):
        """
        Checks the user's password against a provided password - always use
        this rather than directly comparing to
        :attr:`~mongoengine.django.auth.User.password` as the password is
        hashed before storage.
        """
        return check_password(raw_password, self.password)

    
    @classmethod
    def create_user(cls, password, phone_number, username, **kwargs):
        """
        Create (and save) a new user with the given username, password and
        email address.
        """
        now = datetime.timestamp(datetime.now())
        role = kwargs.get("role")
        username = str(kwargs.get("username"))

        user = cls(phone_number=phone_number, joined_date=now, role=role,username=username.lower())

        user.set_password(password)
        user.save()

        # create MassageBox
        message_box = Messagebox.objects.create(user = user.id)
        message_box.save()

        #creating user plan
        plan = Plan.objects.create(user=user.id)
        plan.save()

        return user

    def get_group_permissions(self, obj=None):
        """
        Returns a list of permission strings that this user has through his/her
        groups. This method queries all available auth backends. If an object
        is passed in, only permissions matching this object are returned.
        """
        permissions = set()
        for backend in auth.get_backends():
            if hasattr(backend, "get_group_permissions"):
                permissions.update(backend.get_group_permissions(self, obj))
        return permissions

    def get_all_permissions(self, obj=None):
        return _user_get_all_permissions(self, obj)

    def has_perm(self, perm, obj=None):
        """
        Returns True if the user has the specified permission. This method
        queries all available auth backends, but returns immediately if any
        backend returns True. Thus, a user who has permission from a single
        auth backend is assumed to have permission in general. If an object is
        provided, permissions for this specific object are checked.
        """

        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        return _user_has_perm(self, perm, obj)

    def has_module_perms(self, app_label):
        """
        Returns True if the user has any permissions in the given app label.
        Uses pretty much the same logic as has_perm, above.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        return _user_has_module_perms(self, app_label)

    def get_profile(self):
        """
        Returns site-specific profile for this user. Raises
        SiteProfileNotAvailable if this site does not allow profiles.
        """
        if not hasattr(self, "_profile_cache"):
            from django.conf import settings

            if not getattr(settings, "AUTH_PROFILE_MODULE", False):
                raise auth.SiteProfileNotAvailable(
                    "You need to set AUTH_PROFILE_MO" "DULE in your project settings"
                )
            try:
                app_label, model_name = settings.AUTH_PROFILE_MODULE.split(".")
            except ValueError:
                raise auth.SiteProfileNotAvailable(
                    "app_label and model_name should"
                    " be separated by a dot in the AUTH_PROFILE_MODULE set"
                    "ting"
                )

            try:
                model = models.get_model(app_label, model_name)
                if model is None:
                    raise auth.SiteProfileNotAvailable(
                        "Unable to load the profile "
                        "model, check AUTH_PROFILE_MODULE in your project sett"
                        "ings"
                    )
                self._profile_cache = model._default_manager.using(self._state.db).get(
                    user__id__exact=self.id
                )
                self._profile_cache.user = self
            except (ImportError, ImproperlyConfigured):
                raise auth.SiteProfileNotAvailable
        return self._profile_cache

@python_2_unicode_compatible
class Token(Document):
    """
    This is a mongoengine adaptation of DRF's default Token.

    The default authorization token model.
    """

    key = fields.StringField(required=True)
    user = fields.ReferenceField(User, reverse_delete_rule=mongoengine.CASCADE)
    created = fields.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(Token, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key

class UserSystem(Document):

    id = fields.SequenceField(primary_key=True)

    phone_number = fields.StringField()

    os_type = fields.StringField()

    os_version = fields.StringField()

    device_name = fields.StringField()

    screen_height = fields.StringField()

    screen_width = fields.StringField()

    app_version = fields.StringField()

    device_token = fields.StringField()

    create_date = fields.FloatField(default=lambda : datetime.timestamp(datetime.now()))

    meta = {"ordering": ["-create_date"]}


class Plan(Document):
    VERSION_CHOICES = (
        ("1","Pro"),
        ("2","Premium"),
    )
    id = fields.SequenceField(primary_key=True)
    expire_date = fields.FloatField()
    buy_date = fields.FloatField(default=lambda: datetime.timestamp(datetime.now()))
    plan_version = fields.StringField(choices=VERSION_CHOICES)

