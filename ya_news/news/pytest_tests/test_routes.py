from http import HTTPStatus

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

COMMON_PAGES = [
    ("news:home", None, "get", HTTPStatus.OK),
    ("news:detail", "news_id", "get", HTTPStatus.OK),
    ("users:login", None, "get", HTTPStatus.OK),
    ("users:signup", None, "get", HTTPStatus.OK),
    ("users:logout", None, "post", HTTPStatus.OK),
]

COMMENT_ACTIONS = [
    ("news:edit", "comment_id", "get"),
    ("news:delete", "comment_id", "get"),
]


def get_url(name, arg_name, request):
    """
    Генерирует URL по имени маршрута с аргументом из фикстуры,
    если он указан.
    """
    if not arg_name:
        return reverse(name)
    return reverse(name, args=(request.getfixturevalue(arg_name),))


@pytest.mark.parametrize("name,arg_name,method,expected", COMMON_PAGES)
def test_common_pages_status(request, author_client, name, arg_name, method,
                             expected):
    """Тест статус-кодов основных страниц для авторизованного пользователя."""
    url = get_url(name, arg_name, request)
    client = author_client
    response = getattr(client, method)(url)
    assert response.status_code == expected


@pytest.mark.parametrize("action,arg_name,method", COMMENT_ACTIONS)
def test_comment_action_status_author(request, author_client, action,
                                      arg_name, method):
    """Тест доступа автора к редактированию и удалению комментария."""
    url = get_url(action, arg_name, request)
    response = getattr(author_client, method)(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize("action,arg_name,method", COMMENT_ACTIONS)
def test_comment_action_status_not_author(request, not_author_client, action,
                                          arg_name, method):
    """
    Тест отказа в доступе не-автору
    к редактированию и удалению комментария.
    """
    url = get_url(action, arg_name, request)
    response = getattr(not_author_client, method)(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize("action,arg_name,method", COMMENT_ACTIONS)
def test_comment_action_redirect_anonymous(request, client, action, arg_name,
                                           method):
    """
    Тест редиректа анонимного пользователя
    со страниц действий с комментарием.
    """
    url = get_url(action, arg_name, request)
    login_url = reverse("users:login")
    expected_redirect = f"{login_url}?next={url}"
    response = getattr(client, method)(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_redirect
