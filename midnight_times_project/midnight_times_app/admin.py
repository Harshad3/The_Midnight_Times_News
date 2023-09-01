from django.contrib import admin
from .models import SearchHistory, NewsArticles

admin.site.register(SearchHistory)
admin.site.register(NewsArticles)