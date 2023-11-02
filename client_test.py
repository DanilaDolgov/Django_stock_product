import requests
import json
# # Авторизация пользователя
# response = requests.post(
#     'http://127.0.0.1:8000/user/login',
#     json={ 'email': 'danilevich23555@yandex.ru',
#           'password': 'wishoting24200956dDv1b2n3z0',})
#
#
# # Работа с корзиной
#
# # response = requests.get(
# #     'http://127.0.0.1:8000/basket',
# #     {'token': '099d17042802d4e5d3cd3e97a221f82c49511592'})
#
#
# url='http://127.0.0.1:8000/basket'
# json1={
#       "items": [
#           {
#               "id": 224,
#               "name": "товар1",
#               "quantity": 3,
#               "contact_id": 1
#           }
#       ]
#    }
# print(json.dumps(json1))
# print(json1)
# headers = {"Content-Type": "application/json", "Authorization": "Token 60e7daf91556195e794a9f460655fc5f6c3fc2ff"}
# #
# response = requests.put(url, data=json.dumps(json1), headers=headers)
#
#
# # ---------------------ORDER-----------------
# url='http://127.0.0.1:8000/order'
# json1={
#
#               "id": 1,
#               "contact": 1,
#
#    }
# print(json.dumps(json1))
# print(json1)
# headers = {"Content-Type": "application/json", "Authorization": "Token 60e7daf91556195e794a9f460655fc5f6c3fc2ff"}
# #
# response = requests.post(url, data=json.dumps(json1), headers=headers)
#
# # -----------contact------------------------
# url='http://127.0.0.1:8000/user/contact'
# json1={
#               "user_id": 1,
#               "city": "Москва",
#               "street": "Большая филевская",
#               "house": "23",
#               "structure": "4",
#               "apartment": "681",
#               "phone": "79175066114"
#    }
# print(json.dumps(json1))
# print(json1)
# headers = {"Content-Type": "application/json", "Authorization": "Token 60e7daf91556195e794a9f460655fc5f6c3fc2ff"}

# response = requests.post(url, data=json.dumps(json1), headers=headers)
#
#
# # response = requests.get(
# #     'http://127.0.0.1:8000/basket',
# #     {'token': 'a5424f90317d1fc7a00ff3b9bade0bec05c702bc'})
#
#
# #Регистрация пользователя
# response = requests.post(
#     'http://127.0.0.1:8000/user/register',
#     json={'first_name': 'Данила', 'last_name': 'Долгов', 'email': 'danilevich23555@yandex.ru',
#           'password': 'wishoting24200956dDv1b2n3z0', 'position': 'референт'})
#
#
# response = requests.post(
#     'http://127.0.0.1:8000/partner/update'
# )
#
# # response = requests.get(
# #     'http://127.0.0.1:8000/categories'
# # )