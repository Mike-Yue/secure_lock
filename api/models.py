from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
import datetime

def validate_date(expiry_time):
    if expiry_time < datetime.datetime.now(datetime.timezone.utc):
        raise ValidationError("Expiry Time cannot be in the past!")

class LockUser(AbstractUser):

    def __str__(self):
        return self.email

class Lock(models.Model):

    def __str__(self):
        return self.lock_id

    lock_id = models.CharField(
        max_length=120,
        unique=True,
        null=False,
    )

    display_name = models.CharField(
        max_length=250,
        blank=True,
    )

    master_user = models.ForeignKey(
        LockUser,
        related_name="master_user",
        on_delete=models.CASCADE,
        null=True,
    )

    users = models.ManyToManyField(
        LockUser,
        related_name="users",
        blank=True
    ) 


class Code(models.Model):

    def __str__(self):
        return str(self.code)

    code = models.IntegerField()

    lock = models.ForeignKey(
        Lock,
        on_delete=models.CASCADE,
        null=False,
    )

    expiry_time = models.DateTimeField(
        null=True,
        validators=[validate_date]
    )

    expired = models.BooleanField(
        default=False,
    )

    created_by = models.ForeignKey(
        LockUser,
        related_name="created_by",
        on_delete=models.CASCADE,
        null=True,
    )

    creation_time = models.DateTimeField(
        null=True,
    )

    used_at_time = models.DateTimeField(
        null=True,
    )

