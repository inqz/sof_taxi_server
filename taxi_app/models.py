from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone


class Client(AbstractBaseUser):
    USERNAME_FIELD = 'phone_number'
    surname = models.CharField(max_length=50, verbose_name="Прізвище")
    name = models.CharField(max_length=50, verbose_name="Ім'я")
    phone_number = models.CharField(max_length=20, verbose_name="Номер мобільного")

    def __str__(self):
        return "Клиент №"+str(self.pk)+" "+self.surname+" "+self.name

    class Meta:
        verbose_name_plural = "Клієнти"
        verbose_name = "клієнт"


DRIVER_STATUS = (
    (0, "Недоступний"),
    (1, "Вільний"),
    (2, "Зайнятий"),
    (3, "Тимчасово заблокований"),
    (4, "Заблокований"),
)


class Driver(AbstractBaseUser):
    USERNAME_FIELD = 'login'
    login = models.CharField(max_length=20, unique=True, verbose_name="Логін")
    surname = models.CharField(max_length=50, verbose_name="Прізвище")
    name = models.CharField(max_length=50, verbose_name="Ім'я")
    phone_number = models.CharField(max_length=20, verbose_name="Номер мобільного")
    vehicle_registration_plate = models.CharField(max_length=20, verbose_name="Номер авто")
    money_balance = models.FloatField(verbose_name="Баланс на рахунку", default=0)
    registration_date_time = models.DateTimeField(auto_now_add=True, verbose_name="Дата реєстрації")
    likes = models.PositiveSmallIntegerField(verbose_name="Лайки", default=0)
    dislikes = models.PositiveSmallIntegerField(verbose_name="Дизлайки", default=0)
    fails = models.PositiveSmallIntegerField(verbose_name="Штрафи", default=0)
    last_fail_date = models.DateField(verbose_name="Дата останнього штрафу", null=True, blank=True)
    driver_status = models.PositiveSmallIntegerField(verbose_name="Статус водія", choices=DRIVER_STATUS, default=0)
    driver_lat = models.FloatField(verbose_name="Широта розміщення водія", null=True, blank=True)
    driver_lng = models.FloatField(verbose_name="Довгота розміщення водія", null=True, blank=True)
    radius_of_order_accepting = models.FloatField(verbose_name="Радіус прийому заказів в кілометрах", default=1000.0)

    def __str__(self):
        return self.login

    class Meta:
        verbose_name_plural = "Водії"
        verbose_name = "водій"

    def new_like(self, like: bool = True):
        import sys
        dislikes_limit = Settings.get_settings(SETTINGS_CONSTANTS["DISLIKES_LIMIT"], float(sys.maxsize))
        fails_limit = Settings.get_settings(SETTINGS_CONSTANTS["FAILS_LIMIT"], float(sys.maxsize))
        if like:
            self.likes += 1
        else:
            self.dislikes += 1
            if self.dislikes % dislikes_limit == 0:
                self.driver_status = 3
                self.fails += 1
                self.last_fail_date = timezone.datetime.today()
            elif self.dislikes == fails_limit:
                self.driver_status = 4
                self.fails += 1
                self.last_fail_date = timezone.datetime.today()
        self.save()


ORDER_STATUS = (
    ("new", "Нове замовлення"),
    ("accepted", "Водій прийняв замовлення"),
    ("arrived", "Водій прибув до клієнта"),
    ("executing", "Замовлення виконується"),
    ("finished", "Замовлення виконане"),
    ("canceled", "Замовлення скасовано"),
    ("payed", "Замовлення виконано і оплачено")
)

PAYMENT_TYPE = (
    (0, "Готівка"),
    (1, "Картка"),
)


class Order(models.Model):
    client = models.ForeignKey(Client, verbose_name="Клієнт", null=True, blank=True, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, verbose_name="Водій", null=True, blank=True, on_delete=models.SET_NULL)
    address_from = models.TextField(verbose_name="Точка відправлення", null=True, blank=True)
    address_to = models.TextField(verbose_name="Точка прибуття", null=True, blank=True)
    distance = models.FloatField(verbose_name="Відстань", default=0.0)
    is_child_seat_needed = models.BooleanField(verbose_name="Потрібне дитяче сидіння", default=False)
    is_conditioner_needed = models.BooleanField(verbose_name="Потрібен кондиціонер", default=False)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS, default="new")
    payment_type = models.PositiveSmallIntegerField(verbose_name="Тип оплати", choices=PAYMENT_TYPE, default=0)
    price = models.FloatField(verbose_name="Ціна замовлення", default=0)
    planed_date = models.DateField(verbose_name="Дата замовлення", default=timezone.now)
    planed_time = models.TimeField(verbose_name="Час замовлення", default=timezone.now)

    def __str__(self):
        return self.client.surname+" "+self.client.name+" ("+self.address_from+" -> "+self.address_to+")"

    class Meta:
        verbose_name_plural = "Замовлення"
        verbose_name = "замовлення"


class DriverRejectedOrders(models.Model):
    driver = models.OneToOneField(verbose_name="Водій", on_delete=models.CASCADE, to=Driver)
    orders = models.ManyToManyField(verbose_name="Замовлення", to=Order, blank=True)

    @staticmethod
    def add_new_rejected_order(driver: Driver, order: Order):
        r_order, flag = DriverRejectedOrders.objects.get_or_create(driver=driver)
        r_order.orders.add(order)
        return r_order

    def __str__(self):
        return str(self.driver)

    class Meta:
        verbose_name_plural = "Відхилені водіями замовлення"
        verbose_name = "відхилені водієм замовлення"


class DriverResponsesBook(models.Model):
    driver = models.OneToOneField(Driver, on_delete=models.CASCADE, verbose_name="Водій")
    client = models.OneToOneField(Client, on_delete=models.SET_NULL, verbose_name="Клієнт", null=True, blank=True)
    responses = models.ManyToManyField("ClientResponse", blank=True, verbose_name="Відгуки")

    class Meta:
        verbose_name_plural = "Відгуки про водіїв"
        verbose_name = "відгуки про водія"

    def __str__(self):
        return "Responses about "+self.driver.surname+" "+self.driver.name


RESPONSE_TYPES = (
    (True, "Позитивний"),
    (False, "Негативний"),
)


class ClientResponse(models.Model):
    text = models.TextField(verbose_name="Відгук")
    response_type = models.BooleanField(verbose_name="Тип", choices=RESPONSE_TYPES, default=False)
    date_time = models.DateTimeField(verbose_name="Дата і час", default=timezone.now)

    class Meta:
        verbose_name_plural = "Відгуки"
        verbose_name = "відгук"

    def __str__(self):
        return self.text


SETTINGS_CONSTANTS = {
    "COST_PER_KM": 1,
    "MIN_ORDER_COST": 2,
    "WRITE_OFF_COST": 3,
    "DISLIKES_LIMIT": 4,
    "FAILS_LIMIT": 5,
}

SETTINGS_CONSTANTS_CHOICES = (
    (SETTINGS_CONSTANTS["COST_PER_KM"], "Ціна за кілометр"),
    (SETTINGS_CONSTANTS["MIN_ORDER_COST"], "Мінімальна ціна замовлення"),
    (SETTINGS_CONSTANTS["WRITE_OFF_COST"], "Ціна яка списується з водія за робочий день"),
    (SETTINGS_CONSTANTS["DISLIKES_LIMIT"], "Кількість дизлайків для штрафу"),
    (SETTINGS_CONSTANTS["FAILS_LIMIT"], "Дозволена кількість штрафів"),
)


class Settings(models.Model):
    settings_id = models.PositiveSmallIntegerField(verbose_name="Налаштування", choices=SETTINGS_CONSTANTS_CHOICES,
                                                   primary_key=True)
    value = models.FloatField(verbose_name="Значення", default=0.0)

    @staticmethod
    def get_settings(settings_id: int, default: float=0.0):
        settings = Settings.objects.get_or_create(settings_id=settings_id)
        return default if settings.value == 0.0 else settings.value

    def __str__(self):
        return self.get_settings_id_display()+" - "+str(self.value)

    class Meta:
        verbose_name_plural = "Налаштування"
        verbose_name = "налаштування"
