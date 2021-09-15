from django.db import models

# Create your models here.
class Image(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    keyword = models.CharField(db_column='keyword', max_length=45)
    url = models.CharField(db_column='url', max_length=255)