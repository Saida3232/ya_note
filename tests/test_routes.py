from django.test import TestCase
from notes.models import Note
from django.contrib.auth import get_user_model
from django.urls import reverse
from http import HTTPStatus

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.author = User.objects.create(username='автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Title',
            text='Text',
            author=cls.author)

    def test_available_pages(self):
        list_pages = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in list_pages:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_available_pages_for_login_clients(self):
        list_pages = (('notes:list', None),
                      ('notes:detail', (self.note.slug,)),
                      ('notes:add', None),
                      ('notes:success', None)
        )

        self.client.force_login(self.author)
        for name, args in list_pages:
            with self.subTest(user=self.author, name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_avilible_to_delete_create_note(self):
        user_status = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in user_status:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_anonimus_client(self):
        list_pages = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:add', None))
        login_url = reverse('users:login')
        for name, args in list_pages:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
