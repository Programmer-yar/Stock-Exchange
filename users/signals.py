from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

#Read signals documentation at 'https://docs.djangoproject.com/en/3.1/ref/signals/'

@receiver(post_save, sender=User)  # @receiver(signal, sender), sender is the model class
def create_profile(sender, instance, created, **kwargs): #sender is the model 'User'
    #instance = actual instance being created, 'created' is a boolean and is True if
    #new record was created
	if created:
		Profile.objects.create(user=instance)


@receiver(post_save, sender=User)  # @receiver(signal, sender)
def save_profile(sender, instance, **kwargs):
	instance.profile.save()