from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class SearchHistory(models.Model):
    """
    Model to create the table to store the history of news articles
    """
    keyword = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)


class NewsArticles(models.Model):
    """
    Model to create the table to store the data of News articles and below data
    """
    keyword = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    source_id = models.CharField(max_length=50, null=True, blank=True)
    source_name = models.CharField(max_length=50, null=True, blank=True)
    author = models.CharField(max_length=50, null=True)
    title = models.CharField(max_length=255, null=True)
    description = models.TextField(max_length=700, null=True)
    url = models.TextField(max_length=1000, null=True)
    urlToImage = models.CharField(max_length=500, null=True)
    publishedAt = models.DateTimeField(auto_now_add=False, null=True)
    content = models.TextField(max_length=1000, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
