from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager, AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.shortcuts import render

import json
import yaml
from yaml.loader import SafeLoader
from django.http import HttpResponse

ORDER_STATUS_CHOISES = (
    ('blanket', 'Корзина'),
    ('got', 'Принят'),
    ('confirmed', 'Подтвержден'),
    ('cancelled', 'Отменен'),
    ('assembling', 'Собирается'),
    ('delivering', 'Передан в доставку'),
    ('completed', 'Завершен')
)

USER_TYPE_CHOICES = (
    ('provider', 'Поставщик'),
    ('buyer', 'Покупатель')
)


# Создаем класс менеджера пользователей
class MyUserManager(BaseUserManager):
    def _create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError("Вы не ввели Email")
        if not username:
            raise ValueError("Вы не ввели Логин")
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    # Делаем метод для создание обычного пользователя
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    # Делаем метод для создание админа сайта
    def create_superuser(self, email, username, password):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, username, password, is_staff=True, is_superuser=True)


class User(AbstractBaseUser, PermissionsMixin):
    role = models.CharField(verbose_name='Роль пользователя', max_length=15, choices=USER_TYPE_CHOICES)
    first_name = models.CharField(verbose_name='Имя', max_length=15)
    second_name = models.CharField(verbose_name='Отчество', max_length=15, null=True, blank=True)
    last_name = models.CharField(verbose_name='Фамилия', max_length=15)
    email = models.EmailField(max_length=254, unique=True)
    company = models.CharField(verbose_name='Компания', max_length=30)
    job_title = models.CharField(verbose_name='Должность', max_length=60)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'  # Идентификатор для обращения
    REQUIRED_FIELDS = ['username']  # Список имён полей для Superuser

    objects = MyUserManager()  # Добавляем методы класса MyUserManager

    def __str__(self):
        return self.email

    class Meta:
        ordering = ('email',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        db_table = 'Пользователи'


class Shop(models.Model):
    name = models.CharField(max_length=40, verbose_name='Магазин')
    url = models.URLField(verbose_name='Ссылка на сайт', null=True, blank=True)
    reception_status = models.BooleanField(verbose_name='Прием заказов', default=True)
    provider = models.OneToOneField(User, verbose_name='Поставщик', on_delete=models.CASCADE)

    class Meta:
        ordering = ('name',)
        db_table = 'Магазины'
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'


class Category(models.Model):
    name = models.CharField(verbose_name='Категория', max_length=40)
    shop = models.ManyToManyField(Shop, verbose_name='Магазины', related_name='categories')

    class Meta:
        ordering = ('name',)
        db_table = 'Категории'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Product(models.Model):
    name = models.CharField(verbose_name='Товар', max_length=60)
    category = models.ForeignKey(Category, verbose_name='Категория', related_name='product', on_delete=models.CASCADE)

    class Meta:
        ordering = ('name',)
        db_table = 'Продукты'
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'


class ProductInfo(models.Model):
    product = models.ForeignKey(Product, verbose_name='Товар', related_name='product_info', blank=True,
                                on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='priduct_info', blank=True,
                             on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(verbose_name='Рекомендуемая розничная цена')

    class Meta():
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop'], name='unique product in shop')
        ]


class Parameter(models.Model):
    name = models.CharField(verbose_name='Характеристика', max_length=40)


class ProductParameter(models.Model):
    product = models.ForeignKey(Product, verbose_name='Товар', related_name='product_parameter', blank=True,
                                on_delete=models.CASCADE)
    product_info = models.ForeignKey(ProductInfo, verbose_name='Информация о товаре', related_name='product_parameter',
                                     blank=True, on_delete=models.CASCADE)
    value = models.CharField(verbose_name='Значение', max_length=40)


class Order(models.Model):
    user = models.ForeignKey(User, verbose_name='Покупатель', related_name='order', on_delete=models.CASCADE)
    dt = models.DateTimeField(auto_now_add=True)
    status = models.CharField(verbose_name='Статус заказа', max_length=15, choices=ORDER_STATUS_CHOISES)

    class Meta:
        ordering = ('id',)
        db_table = 'Заказы'
        verbose_name = 'Заказы'
        verbose_name_plural = 'Заказы'


class OrderInfo(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ', related_name='order_info', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Товар', related_name='order_info', on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='order_info', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop'], name='unique product in order')
        ]


class Contacts(models.Model):
    user = models.ForeignKey(User, verbose_name='Имя пользователя', related_name='contacts', on_delete=models.CASCADE)
    phone_number = models.CharField(verbose_name='Телефон', max_length=20)
    city = models.CharField(verbose_name='Город', max_length=15)
    street = models.CharField(verbose_name='Улица', max_length=20)
    building = models.PositiveIntegerField(verbose_name='Номер дома')
    additional_number = models.PositiveIntegerField(verbose_name='Строение', null=True, blank=True)
    litera = models.CharField(verbose_name='Литера', max_length=1, null=True, blank=True)


class UpdateData(models.Model):
    def upload_file(request):
        if request.method == 'POST':
            form = ModelFormWithFileField(request.POST, request.FILES)
            if form.is_valid():
                filetype = request.FILES['product_data'].content_type
                if filetype == 'application/yaml':
                    # file is saved
                    form.save()
                    return HttpResponseRedirect('index')
                else:
                    return JsonResponse({'Status': False, 'Error': 'Допускаются только файлы формата yaml.'},
                                        status=403)
            else:
                return JsonResponse({'Status': False, 'Error': 'Файл не прошел проверку.'}, status=403)

        data = yaml.load(product_data, Loader=SafeLoader)

        shop = Shop.objects.get_or_create(name=data['shop'], user_id=request.user.id)
        for category in data['categories']:
            category_object = Category.objects.get_or_create(id=category['id'], name=category['name'])
            category_object.shops.add(shop.id)
            category_object.save()
        ProductInfo.objects.filter(shop_id=shop.id).delete()
        for item in data['goods']:
            product = Product.objects.get_or_create(name=item['name'], category_id=item['category'])

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

