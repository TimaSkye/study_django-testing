from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

COMMENT_ACTIONS = ['edit', 'delete']
CLIENT_CASES = [
    ('author_client', HTTPStatus.FOUND, 1, 0),
    ('not_author_client', HTTPStatus.NOT_FOUND, 1, 1),
]


@pytest.mark.django_db
def test_user_cant_use_bad_words(news_detail_url, not_author_client):
    """Тест отправки комментария с запрещёнными словами."""
    bad_words_data = {'text': f'Хороший текст, {BAD_WORDS[0]}, еще текст'}
    response = not_author_client.post(news_detail_url, data=bad_words_data)
    form = response.context['form']
    assertFormError(
        form=form,
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.parametrize('action', COMMENT_ACTIONS)
@pytest.mark.parametrize(
    'client_fixture, expected_status, edit_left, delete_left', CLIENT_CASES)
@pytest.mark.django_db
def test_comment_actions_permissions(
        request,
        action,
        client_fixture,
        expected_status,
        edit_left,
        delete_left,
        comment
):
    """Тест прав на редактирование/удаление комментариев."""
    client = request.getfixturevalue(client_fixture)
    url = reverse(f'news:{action}', args=(comment.id,))
    expected_comments = delete_left if action == 'delete' else edit_left
    if action == 'delete':
        response = client.delete(url)
    else:
        response = client.post(url, data={'text': 'Новый текст'})
    assert response.status_code == expected_status
    assert Comment.objects.count() == expected_comments
    if action == 'edit' and client_fixture == 'author_client':
        comment.refresh_from_db()
        assert comment.text == 'Новый текст'
