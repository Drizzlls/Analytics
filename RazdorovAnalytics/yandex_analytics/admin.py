from django.contrib import admin
from .models import YandexData


class YandexDataAdmin(admin.ModelAdmin):
    fields = ["login","apiKey"]

admin.site.register(YandexData, YandexDataAdmin)
