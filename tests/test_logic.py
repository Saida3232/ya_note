from django.test import TestCase, Client
from notes.models import Note
from django.urls import reverse
from django.contrib.auth import get_user_model
from pytils.translit import slugify
from http import HTTPStatus

User = get_user_model()


class TestNotesLogic(TestCase):
    NOTE_TEXT = 'some text about nothing'
    NOTE_TITLE = 'BULSHIT'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Harry Potter')
        cls.url = reverse('notes:add')
        cls.user_client = Client()
        cls.form_data = {'text': cls.NOTE_TEXT, 'title': cls.NOTE_TITLE}

    def test_anonimus_user_cant_create_note(self):
        """Aнонимный пользователь не может создать заметку."""
        self.client.post(self.url, data=self.form_data)
        comments_count = Note.objects.count()
        self.assertEqual(comments_count, 0)

    def test_login_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        self.user_client.force_login(self.user)
        self.user_client.post(self.url, data=self.form_data)
        comments_count = Note.objects.count()
        self.assertEqual(comments_count, 1)
        note1 = Note.objects.get()
        self.assertEqual(note1.text, self.NOTE_TEXT)
        self.assertEqual(note1.title, self.NOTE_TITLE)
        self.assertEqual(note1.author, self.user)


class TestDetaillogic(TestCase):
    NOTE_TEXT = 'hello,guys'
    NEW_NOTE_TEXT = 'goodbay,ladies'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Harry Potter')
        cls.user2 = User.objects.create(username='Draco Malfoy')
        cls.note = Note.objects.create(
            title='New year',
            text=cls.NOTE_TEXT,
            author=cls.user,
        )
        cls.success_url = reverse('notes:success')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.user_client2 = Client()
        cls.user_client2.force_login(cls.user2)
        cls.form_data = {'text': cls.NEW_NOTE_TEXT}

    def test_slug_function(self):
        """Если при создании заметки не заполнен slug, то он формируется автоматически, с помощью функции pytils.translit.slugify."""
        slug_note = slugify(self.note)
        self.assertEqual(slug_note, self.note.slug)

    def test_user_can_delete_note(self):
        response = self.user_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        notes_counts = Note.objects.count()
        self.assertEqual(notes_counts, 0)

    def test_user_cant_delete_notes_of_another_user(self):
        response = self.user_client2.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_counts = Note.objects.count()
        self.assertEqual(notes_counts, 1)

    # def test_user_can_edit_note(self):
    #     response = self.user_client.get(self.edit_url)
    #     self.assertEqual(response.status_code, HTTPStatus.OK)
    #     response = self.user_client.post(self.edit_url, {'text': self.NEW_NOTE_TEXT})
    #     self.note.refresh_from_db()
    #     self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
    def test_user_can_edit_note(self):
        response = self.user_client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/form.html')

    def test_user_cant_edit_comment_of_another_user(self):
        response = self.user_client2.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
