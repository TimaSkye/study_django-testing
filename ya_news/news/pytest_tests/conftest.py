import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def anonymous_client():
    return Client()


@pytest.fixture
def news():
    return News.objects.create(
        title='Тестовый заголовок',
        text='Тестовый текст новости',
    )


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Тестовый комментарий',
    )


@pytest.fixture
def news_id(news):
    return news.id


@pytest.fixture
def comment_id(comment):
    return comment.id


@pytest.fixture
def news_list():
    all_news = [
        News(title=f'Новость {index}', text='Просто текст.')
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def comment_form_data():
    return {'text': 'Текст комментария'}


@pytest.fixture
def news_detail_url(news_id):
    return reverse('news:detail', args=(news_id,))


@pytest.fixture
def comment_delete_url(comment_id):
    return reverse('news:delete', args=(comment_id,))


@pytest.fixture
def comment_edit_url(comment_id):
    return reverse('news:edit', args=(comment_id,))


@pytest.fixture
def url_to_comments(news_detail_url):
    return f'{news_detail_url}#comments'
