# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils import timezone
import os
import time
import random
from uuid import uuid4
import sys
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile


# Avatar picture path
def signature_path(instance, filename):
    upload_to = 'signatures'
    ext = filename.split('.')[-1]
    current_time = int(time.time())
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
    randomstr = ''.join((random.choice(chars)) for x in range(26))
    # get filename
    if instance.pk:
        filename = '{}{}{}.{}'.format(
            instance.pk, randomstr, current_time, ext)
    else:
        # set filename as random string
        filename = '{}{}{}.{}'.format(
            uuid4().hex, randomstr, current_time, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)


class Departement(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


class Profile(models.Model):
    DEPARTMENT_CHOICES = [
        ('', '--'),
        ('audit', 'Audit'),
        ('tax', 'Fiscalité'),
        ('accounting', 'Comptabilité'),
        ('advisory', 'Conseil'),
        ('other', 'Autres'),
    ]
    STATUS_PROFILE = [
        ('collaborator', 'Collaborateur'),
        ('associate', 'Associé'),
        ('senior', 'Sénior'),
        ('admin', 'Administrateur'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    departement = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, verbose_name="Département")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone")
    status = models.CharField(max_length=20, choices=STATUS_PROFILE, verbose_name="Statut")
    signature = models.ImageField(upload_to=signature_path, blank=True, null=True, verbose_name="Signature")
    deleted = models.BooleanField(default=False, verbose_name="Supprimé")
    date_added = models.DateTimeField(auto_now_add=True, verbose_name="Date ajoutée")

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        ordering = ["-date_added"]

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
