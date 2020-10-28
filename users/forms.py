from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class UserRegisterForm(UserCreationForm):
	#Additional fields are defined here
	email = forms.EmailField()
	# 'EmailField' takes 'required' argument which is set to "True by default"

	class Meta:
		"""In Meta class we specify the model with which this form will interact
		Controls configuration for this class"""
		model = User 
		fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
	email = forms.EmailField() 

	class Meta:
		model = User 
		fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
	""" As we dod not want to create additional fields we will directly go to "class:Meta" """
	class Meta:
		model = Profile
		fields = ['image']
			



