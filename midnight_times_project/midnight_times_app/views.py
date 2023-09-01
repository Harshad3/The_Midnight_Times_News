import json
import os
import requests
from datetime import datetime, timedelta, timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import SearchHistory, NewsArticles
import logging

# Initializing config file
CONFIG_FILE = os.path.join(os.getcwd(), "midnight_times_app/config.json")
with open(CONFIG_FILE) as fp:
    CONFIG_DATA = json.load(fp)

# Initializing logging
LOG_FILE = os.path.join(os.getcwd(), "midnight_times_app/app.log")
logging.basicConfig(filename=LOG_FILE,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='a')
LOGGER = logging.getLogger('midnight_times_app')
LOGGER.setLevel(logging.DEBUG)

NEWS_API_KEY = CONFIG_DATA["NEWS_API_KEY"]
NEWS_API_URL = CONFIG_DATA["news_api_url"]


def insert_news_data(keyword, request):
    """
    Standalone method to fetch and insert the News API data into the database
    :param keyword: search keyword from user for which data to be inserted
    :param request: http request sent from user
    """
    LOGGER.info(f"Inserting new data for {keyword} keyword by {request.user} user")
    url = f'{NEWS_API_URL}?q={keyword}&apiKey={NEWS_API_KEY}'
    articles = []
    news_data = {}
    try:
        response = requests.get(url)
        news_data = response.json()
        articles = news_data.get('articles', [])
    except Exception as error:
        LOGGER.critical(f"Error while fetching latest news from news API: {error}")
    if not news_data or news_data.get('status', '') == 'error':
        LOGGER.critical(f"No Data from News API or {news_data.get('message', '')}")
        raise Exception(f"No Data from News API or {news_data.get('message', '')}")
    if articles:
        NewsArticles.objects.filter(keyword=keyword, user=request.user).delete()
    for each_article in articles:
        NewsArticles.objects.create(keyword=keyword,
                                    source_id=each_article.get('source', {}).get('id', '-'),
                                    source_name=each_article.get('source', {}).get(
                                        'source_name', '-'),
                                    author=each_article.get('author', '-'),
                                    title=each_article.get('title', '-'),
                                    description=each_article.get('description', '-'),
                                    url=each_article.get('url', '-'),
                                    urlToImage=each_article.get('urlToImage', '-'),
                                    publishedAt=each_article.get('publishedAt', '-'),
                                    content=each_article.get('content', '-'),
                                    user=request.user)
    LOGGER.info(f"Inserted new data for {keyword} keyword by {request.user} user")


@login_required()
def index(request):
    """
    Inserts data to database based on search keyword from user as a POST data and redirects to
    search_results url with search keyword
    :param request: http request sent from user
    :return: renders index.html page and if POST data received, redirects to search_results url
    """
    if request.method == 'POST':
        keyword = request.POST['keyword']
        LOGGER.info(f"Request received to search {keyword} from user {request.user}")
        SearchHistory.objects.create(keyword=keyword)
        latest_article = NewsArticles.objects.filter(keyword=keyword, user=request.user).order_by(
            '-timestamp').first()
        if latest_article:
            if (datetime.now(timezone.utc) - latest_article.timestamp) > timedelta(
                    minutes=CONFIG_DATA["refresh_threshold_minutes"]):
                insert_news_data(keyword, request)
        else:
            insert_news_data(keyword, request)
        return redirect('search_results', keyword=keyword)
    return render(request, 'index.html')


@login_required()
def search_results(request, keyword):
    """
    Fetch the data from database based on keyword and user logged in
    :param request: http request sent from user
    :param keyword: search keyword from user for which data to be shown
    :return: News articles data to index.html
    """
    articles = NewsArticles.objects.filter(keyword=keyword, user=request.user).order_by(
        '-publishedAt')
    context = {'keyword': keyword, 'articles': articles}
    return render(request, 'index.html', context)


@login_required()
def history(request):
    """
    Fetch top 5 articles for all keywords for logged in user.
    Also refreshes the existing data for all keywords for logged in user based on refresh
    parameter from user
    :param request:
    :return: Top 5 articles for all keywords to history.html page
    """
    # NewsArticles.objects.all().delete()
    # SearchHistory.objects.all().delete()
    keywords = set(NewsArticles.objects.filter(user=request.user).values_list('keyword', flat=True))
    LOGGER.info(f"Received request to view history from user {request.user}")
    if request.GET.get("refresh", '') == 'True':
        LOGGER.warning(f"Refreshing the whole data for user {request.user}")
        for keyword in keywords:
            insert_news_data(keyword, request)

    keyword_data = {}
    for keyword in keywords:
        articles = NewsArticles.objects.filter(keyword=keyword, user=request.user).order_by(
            '-publishedAt')[:5]
        keyword_data[keyword] = articles
    context = {'history': keyword_data}
    return render(request, 'history.html', context)
