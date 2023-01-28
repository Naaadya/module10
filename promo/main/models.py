from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    surname = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    phone = models.IntegerField()

class Company(models.Model):
    name = models.CharField(max_length=200)
    #profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

class ProfileCompany(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE)
    company = models.ForeignKey(Company,on_delete=models.CASCADE)

class House(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)

class Gate(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE)

class REACTION:
    NEUTRAL = 0
    POSITIVE = 1
    NEGATIVE = 2
    CHOICES=(
        (NEUTRAL, 'NEUTRAL'),
        (POSITIVE, 'POSITIVE'),
        (NEGATIVE, 'NEGATIVE')
    )

class Apartment(models.Model):
    house = models.ForeignKey(House, on_delete=models.DO_NOTHING)
    gate = models.ForeignKey(Gate, on_delete=models.DO_NOTHING, null=True)
    number = models.IntegerField(default=0)
    open = models.BooleanField()
    date_time = models.DateTimeField()
    reaction = models.IntegerField(null=True, default=REACTION.NEUTRAL, choices=REACTION.CHOICES)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=16)
    comment = models.TextField(max_length=200)
    def openStr(self):
        if self.open == True:
            return "открыли"
        return "не открыли"
    def reactionStr(self):
        if self.reaction == REACTION.NEUTRAL:
            return "нейтрально"
        if self.reaction == REACTION.POSITIVE:
            return "позитивно"
        if self.reaction == REACTION.NEGATIVE:
            return "негативно"
        return ""