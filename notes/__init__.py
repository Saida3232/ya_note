# test_routes.py
from http import HTTPStatus

from django.urls import reverse


# Указываем в фикстурах встроенный клиент.
def test_home_availability_for_anonymous_user(client):
    # Адрес страницы получаем через reverse():
    url = reverse('notes:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK