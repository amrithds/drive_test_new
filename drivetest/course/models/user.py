from django.db import models
from course.models import Course
from utils.model_util.base_model import BaseModel
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
import random
import datetime
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class User(AbstractUser, BaseModel):
    DRIVER = 1
    INSTRUCTOR = 2
    username_validator = UnicodeUsernameValidator()
    def random_name():
        return str(str(random.randint(10000, 99999))+str(datetime.datetime.now()))
    name=models.CharField(max_length=100, default=None, blank=True, null=True)
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
        default=random_name
    )
    serial_no = models.IntegerField(default=None, null=True, blank=True)
    unique_ref_id=models.CharField(max_length=100, default='superuser')
    course=models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    rank=models.CharField(max_length=50, choices=(
            ("AV" , "AV"),
            ("Rect" , "Rect"),
            ("SEP" , "SEP"),
            ("L Nk" , "L Nk"),
            ("Nk" , "Nk"),
            ("L Hav" , "L Hav"),
            ("Hav" , "Hav"),
            ("Nb Sub" , "Nb Sub"),
            ("Sub" , "Sub"),
            ("Sub Maj" , "Sub Maj"),
            ("Lt" , "Lt"),
            ("Maj" , "Maj"),
            ("Capt" , "Capt"),
            ("Lt Col" , "Lt Col"),
            ("Col" , "Col"),
        ), default='Rect', blank=True, null=True
    )
    unit=models.CharField(max_length=50, default='', blank=True, null=True)
    type=models.IntegerField(choices=(
            (DRIVER, "Driver"),
            (INSTRUCTOR, "Instructor")
        ), default=2)
    REQUIRED_FIELDS = ['unique_ref_id']
    class Meta:
        
        constraints = [
            models.UniqueConstraint(fields=['course', 'unique_ref_id'], name="course_unique_ref_id"),
            models.UniqueConstraint(fields=['course', 'serial_no'], name="course_serial_no"),
        ]
        #unique_together = ('course', 'unique_ref_id')
        #unique_together = ('course', 'unique_ref_id')
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"{self.name}  {self.first_name} {self.last_name}"