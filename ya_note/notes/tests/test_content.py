from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    """Набор тестов контента."""

    NOTE_TITLE = 'Тестовая заметка'
    NOTE_TEXT = 'Текст заметки'
    FORM_PAGES = (
        ('notes:add', None),
        ('notes:edit', 'slug'),
    )

    @classmethod
    def setUpTestData(cls):
        """Набор тестовых данных."""
        cls.author = User.objects.create(username='Автор')
        cls.other_user = User.objects.create(username='Другой пользователь')
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author,
            slug='test-note'
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.other_client = Client()
        cls.other_client.force_login(cls.other_user)

    def test_notes_list_visibility(self):
        """Проверка видимости заметок в списке."""
        test_cases = [
            (self.author_client, True),
            (self.other_client, False)
        ]
        url = reverse('notes:list')
        for client, should_contain in test_cases:
            with self.subTest(should_contain=should_contain):
                response = client.get(url)
                object_list = response.context['object_list']
                self.assertEqual(self.note in object_list, should_contain)

    def test_forms_display(self):
        """Проверка отображения форм."""
        for url_name, arg_name in self.FORM_PAGES:
            with self.subTest(url_name=url_name):
                args = (self.note.slug,) if arg_name else ()
                url = reverse(url_name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
