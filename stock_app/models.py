from django.db import models

from django.contrib.auth.models import User

class File(models.Model):
    file_name = models.DateField(unique=True) 
    #Makes sure that this field has unique entries throughout

    def __str__(self): #str method should only return strings
        return str(self.file_name)

class Company(models.Model):
    file_name = models.ForeignKey(File, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=15)
    closing = models.FloatField()
    volume = models.IntegerField()

    def __str__(self):
        return f'{self.symbol} -> closing price: {self.closing} , volume: {self.volume}'


class Inputs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    volume_input = models.IntegerField()
    date_input = models.CharField(max_length=15)

    def __str__(self):
        return f'Volume : {self.volume_input},  Date :{self.date_input}'

class Result(models.Model):
    """ Stores Result alongwith inputs in database """
    inputs = models.ForeignKey(Inputs, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=15)
    up_down = models.FloatField()
    moving_avg = models.FloatField()

    def __str__(self):
        return f'{self.symbol} --> up_down : {self.up_down}, moving_avg : {self.moving_avg}'


class Upload(models.Model):
    file = models.FileField(upload_to='data base')

    def __str__(self):
        return f'{self.file} Success'



class MailUserInput(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    volume = models.IntegerField(default=0)
    recieve = models.BooleanField(default=False)
    def __str__(self):
        return f'{self.user.username} -> Volume Input: {self.volume}'



class MailUserResults(models.Model):
    inputs = models.ForeignKey(MailUserInput, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=15)
    up_down = models.FloatField()
    moving_avg = models.FloatField()

    def __str__(self):
        return f'{self.symbol} -> {self.up_down} -> {self.moving_avg}'
