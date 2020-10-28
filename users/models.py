from django.db import models
from django.contrib.auth.models import User
from PIL import Image   #from pillow library import image

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE) #One to one relationship with(name of model)
	"""CASCADE means if we delete the the user then also delete the profile but not vice versa"""
	image = models.ImageField(default='default.jpg', upload_to='profile_pics')


	def __str__(self):
		#Dipslays specific itmes with customization
		return f'{self.user.username} Profile'

	#Image resize functionality disabled before placing files on AWS S3	