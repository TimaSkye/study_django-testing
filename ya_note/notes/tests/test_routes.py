from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Набор тестов для проверки маршрутов."""

    HOME_URLS = ('notes:home', 'users:login', 'users:signup')
    AUTH_USER_URLS = ('notes:list', 'notes:success', 'notes:add')
    AUTHOR_ONLY_URLS = ('notes:detail', 'notes:edit', 'notes:delete')

    @classmethod
    def setUpTestData(cls):
        """Набор тестовых данных."""
        cls.user = User.objects.create(username='Обычный пользователь')
        cls.author = User.objects.create(username='Автор заметки')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            slug='test-note',
            author=cls.author
        )
        cls.anon_client = Client()
        cls.user_client = cls.create_authenticated_client(cls.user)
        cls.author_client = cls.create_authenticated_client(cls.author)

    @classmethod
    def create_authenticated_client(cls, user):
        """Создает аутентифицированный клиент."""
        client = Client()
        client.force_login(user)
        return client

    def check_urls_status(self, client, urls, expected_status,
                          slug_required=False):
        """Универсальная проверка статусов для списка URL."""
        for url_name in urls:
            with self.subTest(url_name=url_name):
                args = (self.note.slug,) if slug_required else ()
                url = reverse(url_name, args=args)
                response = client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_anonymous_access(self):
        """Проверка доступности страниц для анонимного пользователя."""
        self.check_urls_status(self.anon_client, self.HOME_URLS,
                               HTTPStatus.OK)
        response = self.anon_client.post(reverse('users:logout'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authenticated_user_access(self):
        """Проверка доступа для авторизованного пользователя."""
        self.check_urls_status(self.user_client, self.AUTH_USER_URLS,
                               HTTPStatus.OK)

    def test_author_access(self):
        """Проверка доступа автора к защищенным страницам."""
        self.check_urls_status(self.author_client, self.AUTHOR_ONLY_URLS,
                               HTTPStatus.OK, slug_required=True)

    def test_non_author_access(self):
        """Проверка доступа НЕ автора к защищенным страницам."""
        self.check_urls_status(self.user_client, self.AUTHOR_ONLY_URLS,
                               HTTPStatus.NOT_FOUND, slug_required=True)

    def test_redirects_for_anonymous(self):
        """Проверка редиректов для анонимных пользователей."""
        login_url = reverse('users:login')
        protected_urls = [
                             (url_name, False) for url_name in
                             self.AUTH_USER_URLS
                         ] + [
                             (url_name, True) for url_name in
                             self.AUTHOR_ONLY_URLS
                         ]
        for url_name, needs_slug in protected_urls:
            with self.subTest(url_name=url_name):
                args = (self.note.slug,) if needs_slug else ()
                url = reverse(url_name, args=args)
                response = self.anon_client.get(url)
                expected_redirect = f'{login_url}?next={url}'
                self.assertRedirects(response, expected_redirect)
