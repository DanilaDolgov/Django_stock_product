from django.shortcuts import render
from distutils.util import strtobool
from django.contrib.auth.backends import ModelBackend
from backend.permissions import IsOwnerOrReadOnly
# Create your views here.
from netology_pd_diplom.celery import get_result
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import IntegrityError
from django.db.models import Q, Sum, F
from django.http import JsonResponse
from requests import get
from rest_framework import viewsets, permissions, renderers, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from ujson import loads as load_json
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, extend_schema_view, OpenApiResponse
from netology_pd_diplom.schema import TokenScheme
from drf_spectacular.types import OpenApiTypes
from backend.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, \
    Contact
from backend.serializers import UserSerializer, CategorySerializer, ShopSerializer, ProductInfoSerializer, \
    OrderItemSerializer, OrderSerializer, ContactSerializer, DummyDetailSerializer, DummyDetailAndStatusSerializer
from backend.test import file_data_yaml
from backend.task import send_mail, new_order
# CodeLogin_app/views.py

from django.views.generic import TemplateView


class Home(TemplateView):
    template_name = "home.html"


class TaskViewGet(APIView):

    def get(self, request, *args, **kwargs):
        task_id = kwargs['task_id']
        task_result = get_result(task_id)
        return Response({'status': task_result.status, 'result': task_result.result})


# class TaskViewCreate(APIView):
#
#     def post(self, request, *args, **kwargs):
#         task = cpu_bound.delay()
#         return Response({'task_id': task.id})


class PartnerUpdate(APIView):
    """
    Класс для обновления прайса от поставщика
    """

    @extend_schema(summary="Добавление нового прайса от поставщика.")
    def post(self, request, *args, **kwargs):
        data = file_data_yaml()[0]
        shop, _ = Shop.objects.get_or_create(name=data['shop'], )
        for category in data['categories']:
            category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
            category_object.shops.add(shop.id)
            category_object.save()
        ProductInfo.objects.filter(shop_id=shop.id).delete()
        for item in data['goods']:
            product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])

            product_info = ProductInfo.objects.create(product_id=product.id,
                                                      price=item['price'],
                                                      price_rrc=item['price_rrc'],
                                                      quantity=item['quantity'],
                                                      shop_id=shop.id)
            for name, value in item['parameters'].items():
                parameter_object, _ = Parameter.objects.get_or_create(name=name)
                ProductParameter.objects.create(product_info_id=product_info.id,
                                                parameter_id=parameter_object.id,
                                                value=value)

        return JsonResponse({'Status': True})


@extend_schema_view(post=extend_schema(summary="Регистрация нового пользователя на сервисе.",
                                       description="""Для регистрации пользователя необходимо отправить post запрос на данный url с параметрами
        {'first_name': 'Имя пользователя', 'last_name': 'Фамилия пользователя', 'email': 'Адрес электронной почты', 
        'password': 'Пароль'}. после регистрации на сервисе необходимо данного пользователя авторизировать и 
        получить token.""", request=UserSerializer,
                                       responses={
                                           status.HTTP_200_OK: UserSerializer,
                                           status.HTTP_400_BAD_REQUEST: DummyDetailSerializer,
                                           status.HTTP_401_UNAUTHORIZED: DummyDetailSerializer,
                                           status.HTTP_403_FORBIDDEN: DummyDetailAndStatusSerializer,
                                       },
                                       parameters=[OpenApiParameter(name='first_name',
                                                                    location=OpenApiParameter.QUERY,
                                                                    type=str,
                                                                    required=False),
                                                   OpenApiParameter(name='last_name',
                                                                    location=OpenApiParameter.QUERY,
                                                                    type=str,
                                                                    required=False),
                                                   OpenApiParameter(name='email',
                                                                    location=OpenApiParameter.QUERY,
                                                                    type=str,
                                                                    required=False),
                                                   OpenApiParameter(name='password',
                                                                    location=OpenApiParameter.QUERY,
                                                                    type=str,
                                                                    required=False),
                                                   OpenApiParameter(name='position',
                                                                    location=OpenApiParameter.QUERY,
                                                                    type=str,
                                                                    required=False)
                                                   ]
                                       ))
class RegisterAccount(APIView):
    """
    Для регистрации покупателей
    """

    # Регистрация методом POST
    def post(self, request):

        # проверяем обязательные аргументы
        if {'first_name', 'last_name', 'email', 'password', 'position'}.issubset(request.data):
            errors = {}

            # проверяем пароль на сложность

            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                # noinspection PyTypeChecker
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
            else:
                # проверяем данные для уникальности имени пользователя
                request.data.update({})
                user_serializer = UserSerializer(data=request.data)
                if user_serializer.is_valid():
                    # сохраняем пользователя
                    user = user_serializer.save()
                    user.set_password(request.data['password'])
                    user.save()
                    task = send_mail.delay('Подтверждение почты', 'Вы зарегистрировались на сайте рога и копыта, '
                                                                  'подтвердите свой адрес!', request.data['email'])
                    return JsonResponse({'Status': True,
                                         'data': 'Пользователь с данными '
                                                 + f"{user.first_name, user.last_name, user.email}"
                                                 + ' успешно зарегистрирован!'})
                # else:
                #     return JsonResponse({'Status': False, 'Errors': user_serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


@extend_schema_view(post=extend_schema(summary="Авторизация нового пользователя на сервисе.",
                                       description="""Для авторизации пользователя необходимо отправить post запрос 
                                       на данный url с параметрами json = {'email': 'Адрес электронной почты', 
                                       'password': 'Пароль'} уже зарегистрированного пользователя. для проверки авторизации
                                       добавить одного пользователя, в противном случае""",
                                       request=UserSerializer,
                                       responses={
                                           status.HTTP_200_OK: UserSerializer,
                                           status.HTTP_400_BAD_REQUEST: DummyDetailSerializer,
                                           status.HTTP_401_UNAUTHORIZED: DummyDetailSerializer,
                                           status.HTTP_403_FORBIDDEN: DummyDetailAndStatusSerializer,
                                       },
                                       parameters=[OpenApiParameter(name='email',
                                                                    location=OpenApiParameter.QUERY,
                                                                    type=str,
                                                                    required=True),
                                                   OpenApiParameter(name='password',
                                                                    location=OpenApiParameter.QUERY,
                                                                    type=str,
                                                                    required=True),
                                                   ]
                                       ))
class LoginAccount(APIView, ModelBackend):
    """
    Класс для авторизации пользователей
    """

    @extend_schema(summary="Авторизация нового пользователя на сервисе и получение token.")
    # Авторизация методом POST
    def post(self, request, *args, **kwargs):

        if {'email', 'password'}.issubset(request.data):

            username = request.data['email']
            password = request.data['password']
            user = self.authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)
                    return JsonResponse({'Status': True, 'Token': token.key})

            return JsonResponse({'Status': False, 'Errors': 'Не удалось авторизовать'})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


@extend_schema(summary="Просмотр информации о магазинах.")
class ShopView(ListAPIView):
    """
    Класс для просмотра списка магазинов
    """

    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer


class ProductInfoView(APIView):
    """
    Класс для поиска товаров
    """

    @extend_schema(summary="Просмотр всех товаров и категорий в магазине.")
    def get(self, request, *args, **kwargs):

        query = Q(shop__state=True)
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')

        if shop_id:
            query = query & Q(shop_id=shop_id)

        if category_id:
            query = query & Q(product__category_id=category_id)

        # фильтруем и отбрасываем дуликаты
        queryset = ProductInfo.objects.filter(
            query).select_related(
            'shop', 'product__category').prefetch_related(
            'product_parameters__parameter').distinct()

        serializer = ProductInfoSerializer(queryset, many=True)

        return Response(serializer.data)


@extend_schema(summary="Просмотр информации о категории товаров.")
class CategoryView(ListAPIView):
    """
    Класс для просмотра категорий
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BasketView(APIView):
    """
    Класс для работы с корзиной пользователя
    """

    @extend_schema(summary="Просмотр корзины пользователя.")
    # получить корзину
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        basket = Order.objects.filter(
            user_id=request.user.id, state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Редактирование корзины пользователя.")
    # редактировать корзину
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_sting = request.data.get('items')
        if items_sting:
            try:
                items_dict = load_json(items_sting)
            except ValueError:
                JsonResponse({'Status': False, 'Errors': 'Неверный формат запроса'})
            else:
                basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
                objects_created = 0
                for order_item in items_dict:
                    order_item.update({'order': basket.id})
                    serializer = OrderItemSerializer(data=order_item)
                    if serializer.is_valid():
                        try:
                            serializer.save()
                        except IntegrityError as error:
                            return JsonResponse({'Status': False, 'Errors': str(error)})
                        else:
                            objects_created += 1

                    else:

                        JsonResponse({'Status': False, 'Errors': serializer.errors})

                return JsonResponse({'Status': True, 'Создано объектов': objects_created})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    @extend_schema(summary="Удаление товаров из корзины пользователя.")
    # удалить товары из корзины
    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_sting = request.data.get('items')
        if items_sting:
            items_list = items_sting.split(',')
            basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
            query = Q()
            objects_deleted = False
            for order_item_id in items_list:
                if order_item_id.isdigit():
                    query = query | Q(order_id=basket.id, id=order_item_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = OrderItem.objects.filter(query).delete()[0]
                return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    @extend_schema(summary="Добавление товаров в корзину пользователя.")
    # добавить позиции в корзину
    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        print(request)
        items_sting = request.data.get('items')
        print(items_sting)
        if items_sting:
            try:
                items_dict = items_sting
            except ValueError:
                JsonResponse({'Status': False, 'Errors': 'Неверный формат запроса'})
            else:
                basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
                objects_updated = 0
                for order_item in items_dict:
                    if type(order_item['id']) == int and type(order_item['quantity']) == int:
                        objects_updated += OrderItem.objects.filter(order_id=basket.id, id=order_item['id']).update(
                            quantity=order_item['quantity'])

                return JsonResponse({'Status': True, 'Обновлено объектов': objects_updated})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class PartnerState(APIView):
    """
    Класс для работы со статусом поставщика
    """

    # получить текущий статус
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        shop = request.user.shop
        serializer = ShopSerializer(shop)
        return Response(serializer.data)

    # изменить текущий статус
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)
        state = request.data.get('state')
        if state:
            try:
                Shop.objects.filter(user_id=request.user.id).update(state=strtobool(state))
                return JsonResponse({'Status': True})
            except ValueError as error:
                return JsonResponse({'Status': False, 'Errors': str(error)})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class PartnerOrders(APIView):
    """
    Класс для получения заказов поставщиками
    """

    @extend_schema(summary="Получение заказов поставщиками.")
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        # if request.user.type != 'shop':
        #     return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        order = Order.objects.filter(
            ordered_items__product_info__shop__user_id=request.user.id).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="Информация по контактам пользователя.",
    ),
    update=extend_schema(
        summary="Изменение контактной информации пользователя.",
    ),
    create=extend_schema(
        summary="Добавление новой контактной информации пользователя.",
        description="""Для добавления контактной информации пользователя необходимо отправить на указанный url json={
              "city": "Город",
              "street": "Улица",
              "house": "Дом",
              "structure": "Корпус",
              "apartment": "Квартира",
              "phone": "Телефон"
   } со следующими заголовками headers = {"Content-Type": "application/json", 
   "Authorization": "Token 3f7e68b155f051e9614e0ecd04152564b2104b22"} где Token выдан при авторизации пользователя.""",
        responses={
            status.HTTP_201_CREATED: ContactSerializer,
            status.HTTP_400_BAD_REQUEST: DummyDetailSerializer,
            status.HTTP_401_UNAUTHORIZED: DummyDetailSerializer,
            status.HTTP_403_FORBIDDEN: DummyDetailAndStatusSerializer,
        },
        parameters=[
            OpenApiParameter(name='city',
                             location=OpenApiParameter.QUERY,
                             type=str,
                             required=True),
            OpenApiParameter(name='street',
                             location=OpenApiParameter.QUERY,
                             type=str,
                             required=True),
            OpenApiParameter(name='house',
                             location=OpenApiParameter.QUERY,
                             type=str,
                             required=True),
            OpenApiParameter(name='structure',
                             location=OpenApiParameter.QUERY,
                             type=str,
                             required=True),
            OpenApiParameter(name='apartment',
                             location=OpenApiParameter.QUERY,
                             type=str,
                             required=True),
            OpenApiParameter(name='phone',
                             location=OpenApiParameter.QUERY,
                             type=str,
                             required=True),
        ]
    ),
    destroy=extend_schema(
        summary="Удаление контактной информации пользователя.",
    ),
    retrieve=extend_schema(
        summary="Вывод одной из контактной информации пользователя.",
    ),

)
class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


# class ContactView(APIView):
#     """
#     Класс для работы с контактами покупателей
#     """
#
#     @extend_schema(summary="Получение информации о контактах пользователя.")
#     # получить мои контакты
#     def get(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
#         contact = Contact.objects.filter(
#             user_id=request.user.id)
#         serializer = ContactSerializer(contact, many=True)
#         return Response(serializer.data)
#
#     @extend_schema(summary="Добавление новой контактной информации пользователя.")
#     # добавить новый контакт
#     def post(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
#
#         if {'city', 'street', 'phone'}.issubset(request.data):
#             # request.data._mutable = True
#             request.data.update({'user': request.user.id})
#             serializer = ContactSerializer(data=request.data)
#
#             if serializer.is_valid():
#                 serializer.save()
#                 return JsonResponse({'Status': True})
#             else:
#                 JsonResponse({'Status': False, 'Errors': serializer.errors})
#
#         return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
#
#     @extend_schema(summary="Удаление контактной информации пользователя.")
#     # удалить контакт
#     def delete(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
#
#         items_sting = request.data.get('items')
#         if items_sting:
#             items_list = items_sting.split(',')
#             query = Q()
#             objects_deleted = False
#             for contact_id in items_list:
#                 if contact_id.isdigit():
#                     query = query | Q(user_id=request.user.id, id=contact_id)
#                     objects_deleted = True
#
#             if objects_deleted:
#                 deleted_count = Contact.objects.filter(query).delete()[0]
#                 return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})
#         return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
#
#     @extend_schema(summary="Изменение контактной информации пользователя.")
#     # редактировать контакт
#     def put(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
#
#         if 'id' in request.data:
#             if request.data['id'].isdigit():
#                 contact = Contact.objects.filter(id=request.data['id'], user_id=request.user.id).first()
#                 print(contact)
#                 if contact:
#                     serializer = ContactSerializer(contact, data=request.data, partial=True)
#                     if serializer.is_valid():
#                         serializer.save()
#                         return JsonResponse({'Status': True})
#                     else:
#                         JsonResponse({'Status': False, 'Errors': serializer.errors})
#
#         return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class OrderView(APIView):
    """
    Класс для получения и размешения заказов пользователями
    """

    @extend_schema(summary="Получение всех заказов пользователей.")
    # получить мои заказы
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        order = Order.objects.filter(
            user_id=request.user.id).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Размещение заказа из корзины пользователя.")
    # разместить заказ из корзины
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if {'id', 'contact'}.issubset(request.data):
            # if request.data['id'].isdigit():
            try:
                is_updated = Order.objects.filter(
                    user_id=request.user.id, id=request.data['id']).update(
                    contact_id=request.data['contact'],
                    state='new')
                print(request.user.id)
                print(request.data['contact'])
                print(is_updated)
            except IntegrityError as error:
                print(error)
                return JsonResponse({'Status': False, 'Errors': 'Неправильно указаны аргументы'})
            else:
                if is_updated:
                    new_order.delay(request.user.id)
                    return JsonResponse({'Status': True})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
