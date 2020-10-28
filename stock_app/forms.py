from django import forms
from .models import Upload, MailUserInput

class UploadFileForm(forms.ModelForm):
    #file = forms.FileField(upload_to='data base')
    #The above command will use inherit class 'forms.Form'
    class Meta:
        model = Upload
        fields = ['file'] #if widgets is added multiple files will be uploaded
        # widgets = {
        #     'file': forms.ClearableFileInput(attrs={'multiple': True}),
        #     #Adds the ability to handle multiple files
        # }

class UpdateUserInputForm(forms.ModelForm):
    class Meta:
        model = MailUserInput
        fields = ['volume', 'recieve']