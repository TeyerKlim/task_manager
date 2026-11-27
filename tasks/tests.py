from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Task


class TaskTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', password='password123')
        self.user2 = User.objects.create_user(username='testuser2', password='password123')
        self.task_user2 = Task.objects.create(
            owner=self.user2,
            title='Чужая задача',
            status='todo',
        )

    def test_redirect_anonymous_user(self):
        response = self.client.get(reverse('tasks:list'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('tasks:list')}")

    def test_list_isolation_and_filter(self):
        Task.objects.create(owner=self.user1, title='Моя задача 1', status='todo')
        Task.objects.create(owner=self.user1, title='Моя задача 2', status='done')
        self.client.login(username='testuser1', password='password123')

        response = self.client.get(reverse('tasks:list'))
        self.assertContains(response, 'Моя задача 1')
        self.assertContains(response, 'Моя задача 2')
        self.assertNotContains(response, 'Чужая задача')

        filtered = self.client.get(reverse('tasks:list'), {'status': 'done'})
        self.assertContains(filtered, 'Моя задача 2')
        self.assertNotContains(filtered, 'Моя задача 1')

    def test_pagination(self):
        for i in range(7):
            Task.objects.create(owner=self.user1, title=f'Задача {i}')
        self.client.login(username='testuser1', password='password123')

        page1 = self.client.get(reverse('tasks:list'))
        self.assertEqual(len(page1.context['object_list']), 5)

        page2 = self.client.get(reverse('tasks:list'), {'page': 2})
        self.assertEqual(len(page2.context['object_list']), 2)

    def test_create_task_valid(self):
        self.client.login(username='testuser1', password='password123')
        response = self.client.post(reverse('tasks:create'), {
            'title': 'Новая задача',
            'description': 'Текст описания',
            'status': 'in_progress',
        })
        self.assertRedirects(response, reverse('tasks:list'))
        task = Task.objects.get(title='Новая задача')
        self.assertEqual(task.owner, self.user1)

    def test_create_task_invalid(self):
        self.client.login(username='testuser1', password='password123')
        response = self.client.post(reverse('tasks:create'), {
            'title': '   ',
            'status': 'wrong_status',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.objects.filter(owner=self.user1).exists())

    def test_forbid_edit_and_delete_foreign_task(self):
        self.client.login(username='testuser1', password='password123')

        edit_resp = self.client.post(
            reverse('tasks:update', kwargs={'pk': self.task_user2.pk}),
            {'title': 'Взлом', 'status': 'done'},
        )
        self.assertEqual(edit_resp.status_code, 404)

        del_resp = self.client.post(
            reverse('tasks:delete', kwargs={'pk': self.task_user2.pk})
        )
        self.assertEqual(del_resp.status_code, 404)
        self.assertTrue(Task.objects.filter(pk=self.task_user2.pk).exists())
