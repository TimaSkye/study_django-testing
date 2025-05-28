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

        cls.anon_client = Client()
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            slug='test-note',
            author=cls.author
        )

    def test_anonymous_access(self):
        """Проверка доступности страниц для анонимного пользователя."""
        for url_name in self.HOME_URLS:
            with self.subTest(url_name=url_name):
                url = reverse(url_name)
                response = self.anon_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.anon_client.post(reverse('users:logout'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authenticated_user_access(self):
        """Проверка доступа для авторизованного пользователя."""
        for url_name in self.AUTH_USER_URLS:
            with self.subTest(url_name=url_name):
                url = reverse(url_name)
                response = self.user_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_pages_author_access(self):
        """Проверка доступа автора к страницам заметки."""
        for url_name in self.AUTHOR_ONLY_URLS:
            with self.subTest(url_name=url_name):
                url = reverse(url_name, args=(self.note.slug,))
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_pages_non_author_access(self):
        """Проверка доступа НЕ автора к страницам заметки."""
        for url_name in self.AUTHOR_ONLY_URLS:
            with self.subTest(url_name=url_name):
                url = reverse(url_name, args=(self.note.slug,))
                response = self.user_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirects_for_anonymous(self):
        """Проверка редиректов для неавторизованных пользователей."""
        login_url = reverse('users:login')
        # Защищённые URL без slug
        protected_urls = [reverse(url) for url in self.AUTH_USER_URLS]
        # Защищённые URL со slug
        protected_urls += [reverse(url, args=(self.note.slug,)) for url in
                           self.AUTHOR_ONLY_URLS]

        for url in protected_urls:
            with self.subTest(url=url):
                redirect_url = f'{login_url}?next={url}'
                response = self.anon_client.get(url)
                self.assertRedirects(response, redirect_url)
