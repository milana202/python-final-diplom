from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager

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

class User(AbstractUser):
    role = models.CharField(verbose_name='Роль пользователя', max_length=15, choices=USER_TYPE_CHOICES)
    first_name = models.CharField(verbose_name='Имя', max_length=15)
    second_name = models.CharField(verbose_name='Отчество', max_length=15, null=True, blank=True)
    last_name = models.CharField(verbose_name='Фамилия', max_length=15)
    email = models.EmailField(max_length=254, unique=True)
    company = models.CharField(verbose_name='Компания', max_length=30)
    job_title = models.CharField(verbose_name='Должность', max_length=60)

    def __str__(self):
        return self.email

    class Meta:
        ordering = ('email',)

class Shop(models.Model):
    name = models.CharField(max_length=40, verbose_name='Магазин')
    url = models.URLField(verbose_name='Ссылка на сайт', null=True, blank=True)
    reception_status = models.BooleanField(verbose_name='Прием заказов', default=True)
    provider = models.OneToOneField(User, verbose_name='Поставщик', on_delete=models.CASCADE)

class Category(models.Model):
    name = models.CharField(verbose_name='Категория', max_length=40)
    shop = models.ManyToManyField(Shop, verbose_name='Магазины', related_name='categories')

class Product(models.Model):
    name = models.CharField(verbose_name='Товар', max_length=60)
    category = models.ForeignKey(Category, verbose_name='Категория', related_name='product', on_delete=models.CASCADE)

class ProductInfo(models.Model):
    product = models.ForeignKey(Product, verbose_name='Товар', related_name='product_info', blank=True, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='priduct_info', blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(verbose_name='Рекомендуемая розничная цена')

    class Meta():
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop'], name=None)
        ]

class Parameter(models.Model):
    name = models.CharField(verbose_name='Характеристика', max_length=40)

class ProductParameter(models.Model):
    product = models.ForeignKey(Product, verbose_name='Товар', related_name='product_parameter', blank=True, on_delete=models.CASCADE)
    product_info = models.ForeignKey(ProductInfo, verbose_name='Информация о товаре', related_name='product_parameter', blank=True, on_delete=models.CASCADE)
    value = models.CharField(verbose_name='Значение', max_length=40)

class Order(models.Model):
    user = models.ForeignKey(User, verbose_name='Покупатель', related_name='order', on_delete=models.CASCADE)
    dt = models.DateTimeField(auto_now_add=True)
    status = models.CharField(verbose_name='Статус заказа', max_length=15, choices=ORDER_STATUS_CHOISES)

class OrderInfo(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ', related_name='order_info', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Товар', related_name='order_info', on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='order_info', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop'], name=None)
        ]

class Contacts(models.Model):
    user = models.ForeignKey(User, verbose_name='Имя пользователя', related_name='contacts', on_delete=models.CASCADE)
    phone_number = models.CharField(verbose_name='Телефон', max_length=20)
    city = models.CharField(verbose_name='Город', max_length=15)
    street = models.CharField(verbose_name='Улица', max_length=20)
    building = models.PositiveIntegerField(verbose_name='Номер дома')
    additional_number = models.PositiveIntegerField(verbose_name='Строение', null=True, blank=True)
    litera = models.CharField(verbose_name='Литера', max_length=1, null=True, blank=True)
