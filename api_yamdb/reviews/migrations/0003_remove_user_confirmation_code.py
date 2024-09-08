from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_user_confirmation_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='confirmation_code',
        ),
    ]
