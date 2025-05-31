from django.urls import reverse

from notes.forms import NoteForm
from .base import BaseTestContent, URLS, NOTE_TITLE, NOTE_TEXT, SLUG


class TestContent(BaseTestContent):
    """Набор тестов контента."""

    def test_author_sees_only_own_notes(self):
        """Автор видит только свою заметку и только одну."""
        url = reverse(URLS['NOTE_LIST'])
        response = self.author_client.get(url)
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), 1)
        note = object_list[0]
        self.assertEqual(note.title, NOTE_TITLE)
        self.assertEqual(note.text, NOTE_TEXT)
        self.assertEqual(note.author, self.author)

    def test_other_user_doesnt_see_author_notes(self):
        """Другой пользователь не видит чужую заметку."""
        url = reverse(URLS['NOTE_LIST'])
        response = self.other_client.get(url)
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), 0)

    def test_forms_display(self):
        """
        Проверка отображения форм на страницах
        добавления и редактирования.
        """
        urls_and_forms = (
            (reverse(URLS['NOTE_ADD']), NoteForm),
            (reverse(URLS['NOTE_EDIT'], args=(SLUG,)), NoteForm),
        )
        for url, form_class in urls_and_forms:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], form_class)
