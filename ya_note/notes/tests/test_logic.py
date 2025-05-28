from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteLogic(TestCase):
    """Набор тестов логики."""

    @classmethod
    def setUpTestData(cls):
        """Набор тестовых данных."""
        cls.user = User.objects.create(username="testUser")
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.author = User.objects.create(username="testAuthor")
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='test_title',
            text='test_text',
            author=cls.author
        )
        cls.add_note_url = reverse('notes:add')

    def test_anonymous_user_cannot_create_note(self):
        """Проверка создания заметки анонимным пользователем."""
        self.client.post(
            self.add_note_url,
            {
                'title': 'Анонимная заметка',
                'text': 'Попытка анонима',
            }
        )
        self.assertFalse(
            Note.objects.filter(title='Анонимная заметка').exists()
        )

    def test_authenticated_user_can_create_note(self):
        """Проверка создания заметки залогиненным пользователем."""
        self.user_client.post(
            self.add_note_url,
            {
                'title': 'Новая заметка',
                'text': 'Содержимое новой заметки',
            }
        )
        self.assertTrue(Note.objects.filter(title='Новая заметка').exists())

    def test_not_unique_slug(self):
        """Проверка возможности создания заметки с повторяющимся slug."""
        initial_count = Note.objects.count()
        response = self.user_client.post(
            self.add_note_url,
            {
                'title': 'Заметка с дубликатом slug',
                'text': 'Содержимое новой заметки',
                'slug': self.note.slug
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn(
            self.note.slug + WARNING,
            str(form.errors['slug'])
        )
        self.assertEqual(Note.objects.count(), initial_count)

    def test_empty_slug(self):
        """Проверка автозаполнения заметки с пустым slug."""
        initial_count = Note.objects.count()
        title = 'Статья с пустым slug'
        response = self.user_client.post(
            self.add_note_url,
            {
                'title': title,
                'text': 'Содержимое новой заметки',
            }
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), initial_count + 1)
        new_note = Note.objects.get(title=title)
        expected_slug = slugify(title)
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Проверка редактирования заметки автором."""
        url = reverse('notes:edit', args=(self.note.slug,))
        title = 'Новый title'
        text = 'Новый text'
        slug = 'new-slug'
        response = self.author_client.post(
            url,
            {
                'title': title,
                'text': text,
                'slug': slug
            }
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, title)
        self.assertEqual(self.note.text, text)
        self.assertEqual(self.note.slug, slug)

    def test_other_user_cant_edit_note(self):
        """Проверка невозможности редактирования чужой заметки."""
        url = reverse('notes:edit', args=(self.note.slug,))
        title = 'Новый title'
        text = 'Новый text'
        slug = 'new-slug'
        response = self.user_client.post(
            url,
            {
                'title': title,
                'text': text,
                'slug': slug
            }
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        """Проверка возможности удаления заметки автором."""
        initial_count = Note.objects.count()
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.author_client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), initial_count - 1)

    def test_other_user_cant_delete_note(self):
        """Проверка невозможности удаления чужой заметки."""
        initial_count = Note.objects.count()
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.user_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), initial_count)
