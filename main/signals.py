from io import BytesIO
import logging
from PIL import Image
from django.core.files.base import ContentFile
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import pre_save, post_save
from .models import OrderItem, ProductImage, Cart

THUMBNAIL_SIZE = (300, 300)

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=ProductImage)
def generate_thumbnail(sender, instance, **kwargs):
    logger.info(
        "Generating thumbnail for product %d",
        instance.product.id,
    )
    image = Image.open(instance.image)
    image = image.convert("RGB")
    image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
    temp_thumb = BytesIO()
    image.save(temp_thumb, "JPEG")
    temp_thumb.seek(0)
    # set save=False, otherwise it will run in an infinite loop
    instance.thumbnail.save(
        instance.image.name,
        ContentFile(temp_thumb.read()),
        save=False,
    )
    temp_thumb.close()


@receiver(user_logged_in)
def merge_carts_if_found(sender, user, request, **kwargs):
    anonymous_cart = getattr(request, "cart", None)
    if anonymous_cart:
        try:
            loggedin_cart = Cart.objects.get(user=user, status=Cart.OPEN)
            for item in anonymous_cart.CartItem_set.all():
                item.cart = loggedin_cart
                item.save()
            anonymous_cart.delete()
            request.cart = loggedin_cart
            logger.info("Merged cart to id %d", loggedin_cart.id)
        except Cart.DoesNotExist:
            anonymous_cart.user = user
            anonymous_cart.save()
            logger.info(
                "Assigned user to cart id %d",
                anonymous_cart.id,
            )


# @receiver(post_save, sender=OrderItem)
# def orderitem_to_order_status(sender, instance, **kwargs):
#     if not instance.order.item.filter(status__lt=OrderItem.SENT).exists():
#         logger.info(
#             "All lines for order %d have been processed. Marking as done.",
#             instance.order.id,
#         )
#         instance.order.status = OrderItem.DONE
#         instance.order.save()
