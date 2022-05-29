from types import CoroutineType
from unicodedata import name
from django.db import models
from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)
from django.core.validators import MinValueValidator
import logging

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField("email address", unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    @property
    def is_employee(self):
        return self.is_active and (
            self.is_superuser
            or self.is_staff
            and self.groups.filter(name="Employees").exists()
        )

    @property
    def is_dispatcher(self):
        return self.is_active and (
            self.is_superuser
            or self.is_staff
            and self.groups.filter(name="Dispatchers").exists()
        )


class ProductTagManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class CategoryManager(models.Manager):
    def get_by_slug(self, slug):
        return self.get(slug=slug)


class ActiveManager(models.Manager):
    def active(self):
        return self.filter(active=True)


class ProductTag(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField(max_length=48)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    objects = ProductTagManager()

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.slug,)


class Category(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField(max_length=48)
    description = models.TextField(blank=True)

    object = CategoryManager

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.slug,)


class Product(models.Model):
    name = models.CharField(max_length=32)
    tags = models.ManyToManyField(ProductTag, blank=True)
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )
    old_price = models.DecimalField(max_digits=6, decimal_places=2)
    new_price = models.DecimalField(max_digits=6, decimal_places=2)
    slug = models.SlugField(max_length=48)
    active = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    rating = models.DecimalField(blank=True, max_digits=5, decimal_places=2, null=True)
    date_updated = models.DateTimeField(auto_now=True)
    objects = ActiveManager()

    class Meta:
        ordering = ("date_updated",)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product-images")
    thumbnail = models.ImageField(upload_to="product-thumbnails", null=True)

    def get_thumbnail(self):
        if self.thumbnail:
            return "http://127.0.0.1:8000" + self.thumbnail.url


class Address(models.Model):
    SUPPORTED_STATES = (
        ("lg", "Lagos"),
        ("kw", "Kwara"),
        ("os", "Osun"),
        ("og", "Ogun"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    address = models.CharField("Address line 1", max_length=60)
    zip_code = models.CharField("ZIP / Postal code", max_length=12)
    city = models.CharField(max_length=60)
    state = models.CharField(max_length=3, choices=SUPPORTED_STATES)

    def __str__(self):
        return ", ".join(
            [
                self.name,
                self.address,
                self.zip_code,
                self.city,
                self.state,
            ]
        )


class Cart(models.Model):
    OPEN = 10
    SUBMITTED = 20
    STATUSES = ((OPEN, "Open"), (SUBMITTED, "Submitted"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    status = models.IntegerField(choices=STATUSES, default=OPEN)

    def is_empty(self):
        return self.cartitem_set.all().count() == 0

    def count(self):
        return sum(i.quantity for i in self.cartitem_set.all())

    def get_total(self):
        total = 0
        for item in self.cartitem_set.all():
            total += item.get_total_item_price()
        return total

    def create_order(self, billing_address, shipping_address, user):
        if not self.user:
            raise exceptions.CartException("Cannot create order without user")
        logger.info(
            "Creating order for cart_id=%d"
            ", shipping_address_id=%d, billing_address_id=%d",
            self.id,
            shipping_address.id,
            billing_address.id,
        )
        order_data = {
            "user": user,
            "billing_name": billing_address.name,
            "billing_address": billing_address.address,
            "billing_zip_code": billing_address.zip_code,
            "billing_city": billing_address.city,
            "billing_state": billing_address.state,
            "shipping_name": shipping_address.name,
            "shipping_address": shipping_address.address,
            "shipping_zip_code": shipping_address.zip_code,
            "shipping_city": shipping_address.city,
            "shipping_state": shipping_address.state,
        }
        order = Order.objects.create(**order_data)
        c = 0
        for line in self.cartitem_set.all():
            for item in range(line.quantity):
                order_item_data = {
                    "order": order,
                    "product": line.product,
                }
            order_line = OrderItem.objects.create(**order_item_data)
        c += 1
        logger.info(
            "Created order with id=%d and items_count=%d",
            order.id,
            c,
        )
        self.status = Cart.SUBMITTED
        self.save()
        return order


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def get_total_item_price(self):
        return self.quantity * self.product.new_price


class Order(models.Model):
    NEW = 10
    PAID = 20
    DONE = 30
    STATUSES = ((NEW, "New"), (PAID, "Paid"), (DONE, "Done"))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUSES, default=NEW)
    billing_name = models.CharField(max_length=60)
    billing_address = models.CharField(max_length=60)
    billing_zip_code = models.CharField(max_length=12)
    billing_city = models.CharField(max_length=60)
    billing_state = models.CharField(max_length=3)
    shipping_name = models.CharField(max_length=60)
    shipping_address = models.CharField(max_length=60)
    shipping_zip_code = models.CharField(max_length=12)
    shipping_city = models.CharField(max_length=60)
    shipping_state = models.CharField(max_length=3)
    date_updated = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    NEW = 10
    PROCESSING = 20
    SENT = 30
    CANCELLED = 40
    STATUSES = (
        (NEW, "New"),
        (PROCESSING, "Processing"),
        (SENT, "Sent"),
        (CANCELLED, "Cancelled"),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="item")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    status = models.IntegerField(choices=STATUSES, default=NEW)


# class Shipping(models.Model):
#     city =
#     fees =
