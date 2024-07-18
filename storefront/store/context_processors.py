from .models import Cart
from uuid import UUID


def cart_id(request):
    cart_id = request.session.get('cart_id', None)

    # Convert to UUID if cart_id is found in session
    if cart_id:
        try:
            cart_id = UUID(cart_id)
        except ValueError:
            cart_id = None

    if not cart_id:
        cart = Cart.objects.create()
        request.session['cart_id'] = str(cart.id)  # Store as string
        cart_id = cart.id

    return {'cart_id': cart_id}
