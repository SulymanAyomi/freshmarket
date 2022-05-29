from . import models


def cart_middleware(get_response):
    def middleware(request):
        if "cart_id" in request.session:
            cart_id = request.session["cart_id"]
            cart = models.Cart.objects.get(id=cart_id)
            product = models.CartItem.objects.filter(cart=cart)[:2]
            request.cart = cart
            request.product = product
        else:
            request.cart = None
            request.product = None

        response = get_response(request)
        return response

    return middleware
