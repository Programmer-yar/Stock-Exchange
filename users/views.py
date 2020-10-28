from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm

def register(request):

	if request.method == 'POST':
		form = UserRegisterForm(request.POST)
		
		if form.is_valid(): 
			form.save()
			username = form.cleaned_data.get('username') #Validated data will be in "form.cleaned" dictionary
			messages.success(request, f'Hi, {username}, your account was created login to continue!')
			#return redirect('blog-home')  #'blog-home is the name of url'
			return redirect('login') 

	else:
		form = UserRegisterForm()

	return render(request, 'users/register.html', {'form':form})
	
@login_required
def profile(request):
	if request.method == 'POST':
		#"instance" prefils the form with existing information
		u_form = UserUpdateForm(request.POST, instance=request.user)
		p_form = ProfileUpdateForm(request.POST,
								   request.FILES,
								   instance=request.user.profile)

		if u_form.is_valid() and p_form.is_valid() :
			u_form.save()
			p_form.save()
			messages.success(request, f' your account has been updated')
			return redirect('profile')

	else:
		u_form = UserUpdateForm(instance=request.user)
		p_form = ProfileUpdateForm(instance=request.user.profile)

	context = { 'u_form' : u_form, 'p_form' : p_form }
	return render(request, 'users/profile.html', context)

