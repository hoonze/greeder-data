from django.db import models

# Create your models here.


class Image(models.Model):
    keyword = models.CharField(db_column='keyword', max_length=45)
    desc = models.CharField(db_column='desc', max_length=255)
    url = models.CharField(db_column='url', max_length=255)

    class Meta:
        managed = False
        db_table = 'image'
