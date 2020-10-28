from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import File, Company, Inputs, Result, MailUserInput, MailUserResults
from .module import Result_func, files_to_database
from easy_pdf.rendering import render_to_pdf_response, render_to_pdf
from .forms import UploadFileForm, UpdateUserInputForm
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import os

import boto3



def home(request):
    dates = File.objects.order_by('-file_name')
    dates = list(dates)
    del dates[-1:-101:-1] #deletes last 100 files 
    #For excluding last 80 or 100 files to maintain remaining files for analysis 
    context = {'dates':dates}
    return render(request, 'stock_app/home.html', context)

@login_required
def result(request):
    if request.method == 'GET':
        volume = request.GET.get('volume') #GET.get('element_name')
        date = request.GET.get('dates')
        days = request.GET.get('days') #Number of days for which moving avg will be calculated
        volume = int(volume)
        days = int(days)

        #Fetches all file names in reverse order i.e most recent dates first
        #and stores them in list
        all_files = File.objects.order_by('-file_name')
        all_files = list(all_files)
        
        #Fetches previous 3 and 100 files from selected date input
        my_date_object = File.objects.get(file_name=date)
        index = all_files.index(my_date_object)
        three_files = all_files[index+1:index+4]
        five_files = all_files[index:6] #includes the selected date as well for cross check
        hundred_files = all_files[index+1:index+days+1]

        #calling the function after the data is ready
        data = Result_func(volume, three_files, five_files, hundred_files)
        results_found = len(data)
        #print(crossings)

        
        if results_found:
            #Storing the inputs and result in the database as requested by client
            logged_in_user = request.user
            user_input = Inputs.objects.create(volume_input=volume, date_input=date,
                                                user=logged_in_user)
            for each_list in data:
                Result.objects.create( inputs=user_input, symbol=each_list[0],
                                       up_down=each_list[1], moving_avg=each_list[2])

        filters = [volume, date]

        context = {'crossings':data, 'results_found':results_found,
                   'filters':filters} 
    return render(request, 'stock_app/result.html', context)


@login_required
def pdf_result(request):

    """ Returns the latest input/result of the user who requested pdf """
    my_inputs = Inputs.objects.filter(user=request.user).latest('date_input')
    my_results = my_inputs.result_set.all()
    context = {'inputs':my_inputs, 'results':my_results}
    # my_pdf = render_to_pdf('stock_app/pdf_result.html', context)
    return render_to_pdf_response(request, 'stock_app/pdf_result.html', context)


@login_required
def upload_file(request):

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file'] #'file' is the name of field already defined in forms.py
            output = files_to_database(file) #returns files already present

            if not output: #checks to see if file is not already in database 
                form.save()
            
            return redirect('upload')
    else:
        form = UploadFileForm()
        flag = False
        if str(request.user) == 'stock_admin':
            flag = True

    return render(request, 'stock_app/upload.html', {'form': form, 'flag':flag})



def downloads(request):
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID') 
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    sesssion = boto3.Session(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    s3 = sesssion.resource('s3')
    bucketName = 'djnago-test-bucket'
    bucket = s3.Bucket(bucketName) #I think each bucket name serves as a module
    media_objects = bucket.objects.filter(Prefix='media/data base')
    #The above filter method should not be confused with django database APIs
    #AWS stores data as 'key:value' pair, key is the path to file
    #e.g key for a picture is, key = 'media/profile_pics/5848152fcef1014c0b5e4967.png'
    base_url = 'https://djnago-test-bucket.s3.ap-south-1.amazonaws.com/media/data base/'
    

    names = []
    for item in media_objects:
        key_name = item.key
        name = key_name.replace('media/data base/', '')
        names.append(name)

    context = {'list':media_objects, 'base_url':base_url, 'names':names}
    return render(request, 'stock_app/downloads.html', context)



@login_required
def my_inputs(request):
    """ Takes input from users, for which results will be sent to their email """
    logged_in_user = request.user
    try:
        user_input = logged_in_user.mailuserinput
        if request.method == 'POST':
            #"instance" prefils the form with existing information
            form = UpdateUserInputForm(instance=user_input, data=request.POST)
            
            if form.is_valid():
                form.save()
                return redirect('inputs')

        else:
            form = UpdateUserInputForm(instance=user_input)

    except:

        if request.method == 'POST':
            form = UpdateUserInputForm(data=request.POST)
            
            if form.is_valid():
                new_input = form.save(commit=False)
                new_input.user = logged_in_user
                new_input.save()
                return redirect('inputs')

        else:
            form = UpdateUserInputForm()


    context = { 'form' : form }
    return render(request, 'stock_app/my_inputs.html', context)



#Added above
# from django.core.mail import EmailMessage
# #settings already imported
# from django.template.loader import render_to_string

def result_email(request):
    """ Should be converted into automated script
     - sends results to users in daily email for their volume input """ 
    filtered_inputs = []
    all_inputs = MailUserInput.objects.all()
    #Fetches all file names in reverse order i.e most recent dates first
    #and stores them in list
    all_files = File.objects.order_by('-file_name')
    all_files = list(all_files)
    date = File.objects.latest('file_name')

    #loop will filter out the user who have subscribed for email
    for each_input in all_inputs:
        if each_input.recieve:
            filtered_inputs.append(each_input)

    for each_input in filtered_inputs:
        volume = each_input.volume
        current_user = each_input.user
        #Fetches previous 3 and 100 files from selected date input and
        # 5 files including present
        three_files = all_files[1:4]
        five_files = all_files[:5] #includes the selected date as well for cross check
        hundred_files = all_files[1:101]

        #calling the function after the data is ready
        data = Result_func(volume, three_files, five_files, hundred_files)
        results_found = len(data)
        filters = [volume, date]
        

        #if results are found writes them to database
        if results_found:

            #Checks to see if previous results are present and deletes them
            #This will happen everyday
            if list(each_input.mailuserresults_set.all()):
                each_input.mailuserresults_set.all().delete()
                for each_list in data:
                    MailUserResults.objects.create(inputs=each_input,
                                                   symbol=each_list[0],
                                                   up_down=each_list[1],
                                                   moving_avg=each_list[2])
            else:
                for each_list in data:
                    MailUserResults.objects.create(inputs=each_input,
                                                   symbol=each_list[0],
                                                   up_down=each_list[1],
                                                   moving_avg=each_list[2])


        #Prepares the email content
        context = {'crossings':data, 'results_found':results_found,
                   'filters':filters} 
        template = render_to_pdf('stock_app/email.html', context)


        email = EmailMessage(
            'Daily Report from Stock Site',
            'Below you will find daily report in pdf' ,
            settings.EMAIL_HOST_USER,
            [current_user.email],)

        file_name = str(date.file_name) + '.pdf'
        email.attach(file_name, template ,"application/pdf")
        email.fail_silently = False
        email.send()

    return render(request, 'stock_app/test.html', { 'success' : 'check your emails' })



