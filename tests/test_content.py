from django.test import TestCase, Client
from notes.models import Note
from django.urls import reverse
from django.contrib.auth import get_user_model


User = get_user_model()
NEWS_COUNT_ON_HOME_PAGE = 10


class TestDetailContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Harry Potter')
        cls.user2 = User.objects.create(username='Draco Malfoy')
        cls.note = Note.objects.create(
            title='some title',
            text='some_text',
            author=cls.user,
        )
        cls.note2 = Note.objects.create(
            title='another title',
            text='another text',
            author=cls.user2,
        )
        cls.url = reverse('notes:list')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.user_client2 = Client()
        cls.user_client2.force_login(cls.user2)

    def test_posts_in_list(self):
        """Тест, который проверяет что отельная запись передается в object_list на страницу списка записей"""
        response = self.user_client.get(self.url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_post_another_user(self):
        """Тест который проверяет что в список заметок одного пользователя не попадают заметки другого пользователя"""
        response = self.user_client.get(self.url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note2, object_list)

    def test_form_in_edit_add_pages(self):
        """На страницы создания и редактирования заметки передаются формы."""
        for name, args in (('notes:add', None), ('notes:edit', (self.note.slug,))):
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.user_client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'form')
