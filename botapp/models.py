from django.db import models


class Dummy(models.Model):
    tetetext = models.CharField(max_length=200)
