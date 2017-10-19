from django.contrib.gis.db.models import GeometryField
from django.contrib.postgres.fields import JSONField
from django.db import models, connection
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.mail import send_mail
from django.utils import timezone

class Article(models.Model):
    id = models.UUIDField(primary_key=True)
    title = models.CharField(max_length=255)
    creation_date = models.DateField()
    content_type = models.CharField(default="html", max_length=255)
    html_content = models.TextField(default="")
    markdown_content = models.TextField(default="")
    is_visible = models.BooleanField()
    track_type = models.CharField(max_length=255)
    geom = GeometryField(srid=4326)
    bbox = JSONField(default=[])
    class Meta:
        index_together = [
            ["track_type", "id"],
        ]

    def compute_bbox(self):
        # TODO: this should be a post-update hook
        with connection.cursor() as cursor:
            cursor.execute("""
                update mainapp_article set bbox=array_to_json(
                array[
                    ST_AsGeoJSON(ST_Envelope(geom))::json->'coordinates'->0->0->0,
                    ST_AsGeoJSON(ST_Envelope(geom))::json->'coordinates'->0->0->1,
                    ST_AsGeoJSON(ST_Envelope(geom))::json->'coordinates'->0->2->0,
                    ST_AsGeoJSON(ST_Envelope(geom))::json->'coordinates'->0->2->1
                ])::jsonb
                where id=%s;
            """, [self.id])

class CustomUserManager(BaseUserManager):

    def _create_user(self, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True,
                                 **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """
    A fully featured User model with admin-compliant permissions that uses
    a full-length email field as the username.

    Email and password are required. Other fields are optional.
    """
    email = models.EmailField('Email address', max_length=254, unique=True)
    name = models.CharField('Name', max_length=30, blank=True)
    is_staff = models.BooleanField('Staff status', default=False,
        help_text='Designates whether the user can log into this admin '
                    'site.')
    is_active = models.BooleanField('Active', default=True,
        help_text='Should the user be treated as active? '
                  'Unselect this instead of deleting accounts.')
    date_joined = models.DateTimeField('Date joined', default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        return self.get_short_name()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.name

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])