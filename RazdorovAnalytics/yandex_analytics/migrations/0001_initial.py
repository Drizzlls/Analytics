# Generated by Django 3.2.9 on 2022-04-10 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login', models.CharField(max_length=50, verbose_name='Логин аккаунта')),
                ('apiKey', models.CharField(max_length=130, verbose_name='API-токен')),
            ],
        ),
    ]