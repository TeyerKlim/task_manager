from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_users_and_tasks(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Task = apps.get_model('tasks', 'Task')

    # Суперпользователь
    User.objects.get_or_create(
        username='admin',
        defaults={
            'password': make_password('Admin12345!'),
            'is_staff': True,
            'is_superuser': True,
        },
    )

    # Первый пользователь
    user1, _ = User.objects.get_or_create(
        username='user1',
        defaults={
            'password': make_password('User12345!'),
            'is_staff': False,
            'is_superuser': False,
        },
    )

    # Второй пользователь
    user2, _ = User.objects.get_or_create(
        username='user2',
        defaults={
            'password': make_password('User12345!'),
            'is_staff': False,
            'is_superuser': False,
        },
    )

    # Задачи
    if not Task.objects.filter(owner=user1).exists():
        statuses = ['todo'] * 6 + ['in_progress'] * 4 + ['done'] * 2
        for i, status in enumerate(statuses, start=1):
            Task.objects.create(
                owner=user1,
                title=f'Задача {i}',
                description=f'Описание задачи {i}',
                status=status,
            )

    if not Task.objects.filter(owner=user2).exists():
        Task.objects.create(
            owner=user2,
            title='Задача второго пользователя',
            description='Тестовая задача user2',
            status='todo',
        )


def delete_users_and_tasks(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(username__in=['admin', 'user1', 'user2']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_users_and_tasks, delete_users_and_tasks),
    ]
