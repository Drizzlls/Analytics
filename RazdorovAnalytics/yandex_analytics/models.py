from django.db import models

# Create your models here.
class YandexData(models.Model):
    login = models.CharField(max_length=50,verbose_name="Логин аккаунта")
    apiKey = models.CharField(max_length=130, verbose_name="API-токен")

    class Meta:
        verbose_name = "Данные из Яндекс.Директ"
        verbose_name_plural = "Данные из Яндекс.Директ"