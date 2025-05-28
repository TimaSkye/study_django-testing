import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count_on_home_page(client, news_list):
    """Тест, на главной не больше NEWS_COUNT_ON_HOME_PAGE новостей."""
    response = client.get(reverse('news:home'))
    assert len(
        response.context['object_list']) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_sorted_by_date(client):
    """Тест новости отсортированы от новых к старым."""
    response = client.get(reverse('news:home'))
    news_dates = [news.date for news in response.context['object_list']]
    assert news_dates == sorted(news_dates, reverse=True)


@pytest.mark.django_db
def test_comments_sorted_by_creation_time(client, news_detail_url):
    """Тест комментарии идут в хронологическом порядке."""
    response = client.get(news_detail_url)
    comments = response.context['news'].comment_set.all()
    assert list(comments) == list(comments.order_by('created'))


@pytest.mark.parametrize(
    'user_client, form_in_context',
    [
        ('client', False),
        ('author_client', True),
    ]
)
@pytest.mark.django_db
def test_comment_form_availability(
        request,
        news_detail_url,
        user_client,
        form_in_context):
    """Тест доступности формы для разных пользователей."""
    client = request.getfixturevalue(user_client)
    response = client.get(news_detail_url)
    assert ('form' in response.context) is form_in_context
    if form_in_context:
        assert isinstance(response.context['form'], CommentForm)
