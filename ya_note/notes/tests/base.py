from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()

NOTE_TITLE = 'Тестовая заметка'
NOTE_TEXT = 'Текст заметки'
SLUG = 'test-note'
NEW_SLUG = 'new-slug'

URLS = {
    'NOTE_LIST': 'notes:list',
    'NOTE_ADD': 'notes:add',
    'NOTE_EDIT': 'notes:edit',
    'NOTE_DETAIL': 'notes:detail',
    'NOTE_DELETE': 'notes:delete',
    'NOTE_SUCCESS': 'notes:success',
}

ROUTE_URLS = {
    'HOME_URLS': ('notes:home', 'users:login', 'users:signup'),
    'AUTH_USER_URLS': ('notes:list', 'notes:success', 'notes:add'),
    'AUTHOR_ONLY_URLS': ('notes:detail', 'notes:edit', 'notes:delete'),
}


class BaseTestContent(TestCase):
    """Базовый класс для тестов контента."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.other_user = User.objects.create(username='Другой пользователь')
        cls.note = Note.objects.create(
            title=NOTE_TITLE,
            text=NOTE_TEXT,
            author=cls.author,
            slug=SLUG
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.other_client = Client()
        cls.other_client.force_login(cls.other_user)


class LogicTestBase(TestCase):
    """Базовый класс для тестов логики заметок."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Пользователи
        cls.user = User.objects.create(username="Обычный пользователь")
        cls.author = User.objects.create(username="Автор заметки")

        # Клиенты
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        # Тестовая заметка
        cls.note = Note.objects.create(
            title=NOTE_TITLE,
            text=NOTE_TEXT,
            author=cls.author,
            slug=SLUG
        )

        # URL-адреса
        cls.add_note_url = reverse(URLS['NOTE_ADD'])
        cls.edit_note_url = reverse(URLS['NOTE_EDIT'], args=(SLUG,))
        cls.delete_note_url = reverse(URLS['NOTE_DELETE'], args=(SLUG,))


class RoutesTestBase(TestCase):
    """Базовый класс для тестов маршрутов."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Обычный пользователь')
        cls.author = User.objects.create(username='Автор заметки')
        cls.note = Note.objects.create(
            title=NOTE_TITLE,
            text=NOTE_TEXT,
            slug=SLUG,
            author=cls.author
        )
        cls.anon_client = Client()
        cls.user_client = cls.create_authenticated_client(cls.user)
        cls.author_client = cls.create_authenticated_client(cls.author)

    @classmethod
    def create_authenticated_client(cls, user):
        client = Client()
        client.force_login(user)
        return client
