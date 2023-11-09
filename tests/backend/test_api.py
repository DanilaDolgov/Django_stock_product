import json

import pytest
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from model_bakery import baker

from backend.models import User, Contact


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user('admin@gmali.com')


@pytest.fixture
def data():
    return [{'first_name': 'test', 'last_name': 'test_1', 'email': 'test_2@test.ru',
             'password': 'test', 'position': 'test'}, {'email': 'test_2@test.ru',
                                                       'password': 'test_1', }, {
                "city": "test_1",
                "street": "test_2",
                "house": "test_3",
                "structure": "test_4",
                "apartment": "test_5",
                "phone": "test_6"
            }]


@pytest.fixture
def user_factory():
    def factory(*args, **kwargs):
        return baker.make(User, *args, **kwargs)

    return factory


@pytest.mark.django_db
def test_api_register(client, user_factory):
    users = user_factory(_quantity=1)
    for user in users:
        resp = client.post('/user/register', data={'first_name': f'{user.first_name}', 'last_name': f'{user.last_name}',
                                                   'email': f'{user.email}', 'password': f'{user.password}',
                                                   'position': f'{user.position}'}, format='json')
        assert resp.status_code == 200


@pytest.mark.django_db
def test_api_authorization(client, data):
    resp = client.post('/user/login', data=data[1])
    assert resp.status_code == 200


@pytest.mark.django_db
def test_add_contacts(client, user, data):
    count = Contact.objects.count()
    token, _ = Token.objects.get_or_create(user=user)

    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    resp = client.post('/user/contactsviewset', data=data[2])

    assert resp.status_code == 201
    assert Contact.objects.count() == count + 1
