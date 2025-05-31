from http import HTTPStatus

from django.urls import reverse

from .base import RoutesTestBase, ROUTE_URLS


class TestRoutes(RoutesTestBase):
    """Набор тестов для проверки маршрутов."""

    def check_urls_status(self, client, urls, expected_status,
                          slug_required=False):
        """Универсальная проверка статусов для списка URL."""
        for url_name in urls:
            with self.subTest(url_name=url_name):
                args = (self.note.slug,) if slug_required else ()
                url = reverse(url_name, args=args)
                response = client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_status_codes(self):
        """
        Проверяет все возможные коды ответа
        для разных типов пользователей.
        """
        # Анонимный пользователь.
        self.check_urls_status(self.anon_client, ROUTE_URLS['HOME_URLS'],
                               HTTPStatus.OK)
        response = self.anon_client.post(reverse('users:logout'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Авторизованный пользователь (не автор).
        self.check_urls_status(self.user_client, ROUTE_URLS['AUTH_USER_URLS'],
                               HTTPStatus.OK)
        self.check_urls_status(
            self.user_client,
            ROUTE_URLS['AUTHOR_ONLY_URLS'],
            HTTPStatus.NOT_FOUND,
            slug_required=True
        )

        # Автор заметки.
        self.check_urls_status(
            self.author_client,
            ROUTE_URLS['AUTHOR_ONLY_URLS'],
            HTTPStatus.OK,
            slug_required=True
        )

    def test_redirects(self):
        """Проверяет все сценарии редиректов для анонимных пользователей."""
        login_url = reverse('users:login')
        protected_urls = [
            *[(url, False) for url in ROUTE_URLS['AUTH_USER_URLS']],
            *[(url, True) for url in ROUTE_URLS['AUTHOR_ONLY_URLS']]
        ]

        for url_name, needs_slug in protected_urls:
            with self.subTest(url_name=url_name):
                args = (self.note.slug,) if needs_slug else ()
                url = reverse(url_name, args=args)
                response = self.anon_client.get(url)
                expected_redirect = f'{login_url}?next={url}'
                self.assertRedirects(response, expected_redirect)
