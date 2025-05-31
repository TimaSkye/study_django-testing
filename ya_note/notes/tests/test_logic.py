from http import HTTPStatus

from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from .base import LogicTestBase, NOTE_TITLE, NOTE_TEXT, URLS, SLUG, NEW_SLUG
from ..models import Note


class TestNoteLogic(LogicTestBase):
    """Набор тестов логики."""

    def test_anonymous_user_cannot_create_note(self):
        """Проверка создания заметки анонимным пользователем."""
        initial_count = Note.objects.count()
        self.client.post(
            self.add_note_url,
            {'title': 'Анонимная заметка', 'text': 'Попытка анонима'}
        )
        self.assertEqual(Note.objects.count(), initial_count)

    def test_authenticated_user_can_create_note(self):
        """Проверка создания заметки залогиненным пользователем."""
        initial_count = Note.objects.count()
        form_data = {
            'title': 'Новая заметка',
            'text': 'Содержимое новой заметки',
            'slug': NEW_SLUG
        }
        response = self.user_client.post(self.add_note_url, form_data)
        self.assertRedirects(response, reverse(URLS['NOTE_SUCCESS']))
        self.assertEqual(Note.objects.count(), initial_count + 1)

        new_note = Note.objects.get(slug=NEW_SLUG)
        self.assertEqual(new_note.title, form_data['title'])
        self.assertEqual(new_note.text, form_data['text'])
        self.assertEqual(new_note.author, self.user)

    def test_not_unique_slug(self):
        """Проверка возможности создания заметки с повторяющимся slug."""
        initial_count = Note.objects.count()
        response = self.user_client.post(
            self.add_note_url,
            {
                'title': 'Заметка с дубликатом slug',
                'text': 'Содержимое новой заметки',
                'slug': SLUG  # Используем константу из base.py
            }
        )
        self.assertEqual(Note.objects.count(), initial_count)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertTrue(form.has_error('slug'))
        self.assertIn(WARNING, form.errors['slug'][0])

    def test_empty_slug(self):
        """Проверка автозаполнения заметки с пустым slug."""
        initial_count = Note.objects.count()
        title = 'Статья с пустым slug'
        response = self.user_client.post(
            self.add_note_url,
            {'title': title, 'text': 'Содержимое новой заметки'}
        )
        self.assertRedirects(response, reverse(URLS['NOTE_SUCCESS']))
        self.assertEqual(Note.objects.count(), initial_count + 1)

        new_note = Note.objects.get(title=title)
        expected_slug = slugify(title)
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Проверка редактирования заметки автором."""
        new_data = {
            'title': 'Новый title',
            'text': 'Новый text',
            'slug': NEW_SLUG
        }
        response = self.author_client.post(self.edit_note_url, new_data)
        self.assertRedirects(response, reverse(URLS['NOTE_SUCCESS']))

        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, new_data['title'])
        self.assertEqual(updated_note.text, new_data['text'])
        self.assertEqual(updated_note.slug, new_data['slug'])
        self.assertEqual(updated_note.author, self.author)

    def test_other_user_cant_edit_note(self):
        """Проверка невозможности редактирования чужой заметки."""
        initial_data = {
            'title': NOTE_TITLE,
            'text': NOTE_TEXT,
            'slug': SLUG
        }
        new_data = {
            'title': 'Новый title',
            'text': 'Новый text',
            'slug': NEW_SLUG
        }
        response = self.user_client.post(self.edit_note_url, new_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(note_from_db.title, initial_data['title'])
        self.assertEqual(note_from_db.text, initial_data['text'])
        self.assertEqual(note_from_db.slug, initial_data['slug'])
        self.assertEqual(note_from_db.author, self.author)

    def test_author_can_delete_note(self):
        """Проверка возможности удаления заметки автором."""
        initial_count = Note.objects.count()
        response = self.author_client.post(self.delete_note_url)
        self.assertRedirects(response, reverse(URLS['NOTE_SUCCESS']))
        self.assertEqual(Note.objects.count(), initial_count - 1)
        with self.assertRaises(ObjectDoesNotExist):
            Note.objects.get(id=self.note.id)

    def test_other_user_cant_delete_note(self):
        """Проверка невозможности удаления чужой заметки."""
        initial_count = Note.objects.count()
        response = self.user_client.post(self.delete_note_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), initial_count)
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())
