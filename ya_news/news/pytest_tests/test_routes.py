from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

COMMON_PAGES = [
    ("news:home", None),
    ("news:detail", "news_id"),
    ("users:login", None),
    ("users:signup", None),
]
COMMENT_ACTIONS = ["news:edit", "news:delete"]
CLIENT_CASES = [
    ("not_author_client", HTTPStatus.NOT_FOUND),
    ("author_client", HTTPStatus.OK),
]


@pytest.mark.django_db
@pytest.mark.parametrize("name, args_fixture", COMMON_PAGES)
def test_pages_availability(client, name,
                            args_fixture, news_id):
    """Тест доступности основных страниц."""
    url_args = (news_id,) if args_fixture == "news_id" else ()
    url = reverse(name, args=url_args or None)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_logout_availability(client):
    """Тест доступности выхода через POST."""
    response = client.post(reverse("users:logout"))
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize("client_fixture, expected", CLIENT_CASES)
@pytest.mark.parametrize("action", COMMENT_ACTIONS)
def test_comment_actions_access(
        request, action,
        client_fixture, expected,
        comment):
    """Тест прав доступа к действиям с комментариями."""
    client = request.getfixturevalue(client_fixture)
    url = reverse(action, args=(comment.id,))
    response = client.get(url)
    assert response.status_code == expected


@pytest.mark.django_db
@pytest.mark.parametrize("action", COMMENT_ACTIONS)
def test_redirects_for_anonymous(client, action, comment):
    """Тест редиректов для анонимных пользователей."""
    url = reverse(action, args=(comment.id,))
    login_url = reverse("users:login")
    expected_url = f"{login_url}?next={url}"
    response = client.get(url)
    assertRedirects(response, expected_url)
