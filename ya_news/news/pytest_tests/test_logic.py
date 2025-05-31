from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_authorized_user_can_create_comment(news_detail_url, author_client,
                                            author):
    """Авторизованный пользователь может создать комментарий."""
    form_data = {'text': 'Тестовый Комментарий.'}
    response = author_client.post(news_detail_url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1
    comment = Comment.objects.first()
    assert comment.text == form_data['text']
    assert comment.author == author


def test_anonymous_user_cannot_create_comment(news_detail_url, client):
    """Анонимный пользователь не может создать комментарий."""
    form_data = {'text': 'Комментарий от анонима'}
    response = client.post(news_detail_url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client, comment):
    """Автор может редактировать свой комментарий."""
    url = reverse('news:edit', args=(comment.id,))
    form_data = {'text': 'Обновленный текст комментария'}
    old_author = comment.author
    old_created = comment.created
    response = author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == old_author
    assert comment.created == old_created


def test_not_author_cannot_edit_comment(not_author_client, comment):
    """Не автор не может редактировать чужой комментарий."""
    url = reverse('news:edit', args=(comment.id,))
    form_data = {'text': 'Попытка взлома'}
    old_text = comment.text
    old_author = comment.author
    old_created = comment.created
    response = not_author_client.post(url, data=form_data)
    assert response.status_code in (HTTPStatus.NOT_FOUND,
                                    HTTPStatus.FORBIDDEN)
    comment.refresh_from_db()
    assert comment.text == old_text
    assert comment.author == old_author
    assert comment.created == old_created


def test_author_can_delete_comment(author_client, comment):
    """Автор может удалить свой комментарий."""
    url = reverse('news:delete', args=(comment.id,))
    count_before = Comment.objects.count()
    response = author_client.delete(url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == count_before - 1
    assert not Comment.objects.filter(id=comment.id).exists()


def test_not_author_cannot_delete_comment(not_author_client, comment):
    """Не автор не может удалить чужой комментарий."""
    url = reverse('news:delete', args=(comment.id,))
    count_before = Comment.objects.count()
    old_text = comment.text
    old_author = comment.author
    old_created = comment.created
    response = not_author_client.delete(url)
    assert response.status_code in (HTTPStatus.NOT_FOUND,
                                    HTTPStatus.FORBIDDEN)
    assert Comment.objects.count() == count_before
    comment.refresh_from_db()
    assert comment.text == old_text
    assert comment.author == old_author
    assert comment.created == old_created


def test_user_cant_use_bad_words(news_detail_url, not_author_client):
    """Тест отправки комментария с запрещёнными словами."""
    form_data = {'text': f'Хороший текст, {BAD_WORDS[0]}, еще текст'}
    response = not_author_client.post(news_detail_url, data=form_data)
    form = response.context['form']
    assertFormError(form=form, field='text', errors=WARNING)
    assert Comment.objects.count() == 0
