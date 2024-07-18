from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from store.forms import OrderForm
from store.permissions import IsAdminOrReadOnly
from store.pagination import DefaultPagination
from django.shortcuts import redirect, render
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth.models import AnonymousUser
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import generics
from rest_framework import status
from .filters import ProductFilter
from django.contrib.auth.decorators import login_required
from .models import *
from .serializers import *
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.mail import send_mail, BadHeaderError


class ProductViewSet(ModelViewSet, generics.RetrieveAPIView):
    queryset = Product.objects.prefetch_related('images').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']
    renderer_classes = [TemplateHTMLRenderer]
    # ^used to render customer templates

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def products_page(self, request):
        products = self.get_queryset()

        return Response({'products': products}, template_name='store/products_page.html')

    def retrieve(self, request, *args, **kwargs):
        product = self.get_object()
        cart_id = request.session.get('cart_id')
        return Response({'product': product}, template_name='store/product_detail.html')


class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(
        products_count=Count('products')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']):
            return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}


class CartViewSet(CreateModelMixin,
                  RetrieveModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        cart_id = str(serializer.instance.id)
        request.session['cart_id'] = str(cart_id)

        # combine cart_id with serializer data
        response_data = serializer.data
        response_data['cart_id'] = cart_id

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    def get_serializer_context(self):

        # This method returns a context dictionary to the serializer
        context = super().get_serializer_context()
        context.update({'request': self.request})
        # send request data over to extract image
        return context


class CartItemViewSet(ModelViewSet, generics.RetrieveAPIView):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects \
            .filter(cart_id=self.kwargs['cart_pk']) \
            .select_related('product')

    @action(detail=True, methods=['post', 'patch', 'delete'], url_path='cart_item_update')
    def cart_item_update(self, request, pk=None, cart_pk=None):
        if request.data.get('_method') == 'PATCH':
            quantity = request.data.get('quantity')
            # This retrieves the CartItem instance based on the 'pk' from the URL.
            cart_item = self.get_object()
            cart_item.quantity = quantity
            cart_item.save()
            cart_url = reverse('store:cart-items-cart-page',
                               kwargs={'cart_pk': cart_pk})
            return HttpResponseRedirect(cart_url)

        elif request.data.get('_method') == 'DELETE':
            # This retrieves the CartItem instance based on the 'pk' from the URL.
            cart_item = self.get_object()
            cart_item.delete()
            cart_url = reverse('store:cart-items-cart-page',
                               kwargs={'cart_pk': cart_pk})
            return HttpResponseRedirect(cart_url)

    @action(detail=False, methods=['get'], renderer_classes=[TemplateHTMLRenderer],
            # permission_classes=([IsAuthenticated])
            )
    def checkout_page(self, request, pk=None, *args, **kwargs):
        # or however you store your token
        token = request.COOKIES.get('access_token')
        if not token:
            # Redirect to the sign-in page with the 'next' parameter
            return redirect(f'/accounts/login/?next={request.path}')

        form = OrderForm()

        cart_id = kwargs.get('cart_pk')
        if not cart_id:
            return Response({'error': 'Cart ID not found in session'}, status=status.HTTP_404_NOT_FOUND)

        try:
            cart = Cart.objects.get(pk=cart_id)
            cart_id = cart.id

            cart_items = cart.items.all()
            cart_total = sum(
                [item.product.unit_price * item.quantity for item in cart_items])
            context = {'form': form, 'cart': cart,
                       'cart_items': cart_items, 'cart_id': cart_id,
                       'total': cart_total}
            return Response(context, template_name='store/checkout_page.html')
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], renderer_classes=[TemplateHTMLRenderer])
    def cart_page(self, request, pk=None, **kwargs):
        cart_id = request.session.get('cart_id')

        if not cart_id:
            # No cart exists in the session, create a new cart
            cart = Cart.objects.create()
            cart_id = str(cart.id)
            request.session['cart_id'] = cart_id
        else:
            try:
                cart = Cart.objects.get(pk=cart_id)

            except Cart.DoesNotExist:
                # Cart does not exist in the database, create a new cart
                cart = Cart.objects.create()
                cart_id = str(cart.id)
                request.session['cart_id'] = cart_id

        cart_items = cart.items.all()
        cart_total = sum(
            [item.product.unit_price * item.quantity for item in cart_items])

        return Response({'cart': cart, 'cart_items': cart_items, 'cart_id': cart_id, 'total': cart_total}, template_name='store/cart_page.html')


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['GET', 'PUT'])
    def me(self, request):

        user_id = self.request.user.id
        customer = Customer.objects.get(user_id=user_id)
        cart_id = request.session.get('cart_id')
        print(customer)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            # context = {'customer': customer, 'cart_id' : cart_id}
            customer_data = serializer.data
            customer_data['cart_id'] = cart_id
            print(customer_data)
            return Response(customer_data)

        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        customer_id = Customer.objects.only(
            'id').get(user_id=user.id)
        return Order.objects.filter(customer_id=customer_id)

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [AllowAny()]

    @action(detail=False, methods=['GET', 'POST'])
    def post_order(self, request, *args, **kwargs):
        print("post_order method called")
        if request.user.is_authenticated:
            print("User is authenticated")
            serializer = CreateOrderSerializer(
                data=request.data,
                context={'user_id': request.user.id,
                         'cart_id': request.data.get('cart_id')}
            )

            print("Serializer created")
            serializer.is_valid(raise_exception=True)
            print("Serializer is valid")
            order = serializer.save()
            print(f"Order saved: {order}")
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        else:
            print("User is not authenticated")
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['GET'])
    def get_all_orders(self, request, *args, **kwargs):

        user = request.user

        if not user.is_authenticated:
            # If the user is not authenticated, return a 401 Unauthorized response
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        if user.is_staff:
            orders = Order.objects.all()
        else:
            try:
                customer = Customer.objects.get(user=user)
                orders = Order.objects.prefetch_related(
                    'items__product__images').filter(customer=customer)
            except Customer.DoesNotExist:
                # Handle the case where the customer does not exist for the user
                return Response({"detail": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], renderer_classes=[TemplateHTMLRenderer])
    def get_order(self, request, *kwargs):

        # order_id = kwargs['order_pk']

        user = self.request.user
        customer = Customer.objects.get(user__id=user.id)
        order = Order.objects.filter(
            customer=customer).order_by('-placed_at').first()
        serializer = OrderSerializer(order)
        orderData = serializer.data

        return (orderData)


def order_success_page(request):
    user = request.user
    customer = Customer.objects.get(user__id=user.id)
    order = Order.objects.filter(
        customer=customer).order_by('-placed_at').first()
    serializer = OrderSerializer(order)
    orderData = serializer.data

    # if 'cart_id' in request.session:
    #     del request.session['cart_id']

    return render(request, 'store/order_success.html', {'order': orderData})


def order_form_view(request):

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Extract data from form
            phone = form.cleaned_data['phone']
            # birth_date = form.cleaned_data['birth_date']
            street = form.cleaned_data['street']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']

            # Update or create customer and address objects
            customer, created = Customer.objects.update_or_create(
                user=request.user,
                defaults={'phone': phone}
            )
            Address.objects.update_or_create(
                customer=customer,
                defaults={'street': street, 'city': city, 'state': state}
            )

            # # Redirect to a success page
            return HttpResponseRedirect('/store/order_success')

    else:
        form = OrderForm()

    return render(request, 'store/checkout_page.html', {'form': form})


@login_required  # Require authentication for this view
def post_order(request):
    user = request.user
    print(user)

    # Check if the user is authenticated and not an AnonymousUser
    if not user.is_authenticated or isinstance(user, AnonymousUser):
        return Response({'error': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'POST':
        serializer = CreateOrderSerializer(
            data=request.POST,  # Use request.POST to access form data
            context={
                'user_id': user.id,
                'cart_id': request.POST.get('cart_id')
            }
        )

    # Check if the data is valid (raises an exception if not)
    if serializer.is_valid(raise_exception=True):

        # Save the new order
        order = serializer.save()

        # Send order confirmation email
        order_confirmation_email(order)
        # Redirect to a success page or perform any other necessary actions
        # Replace 'success_page' with your actual success page URL
        return redirect('/store/order_success')


def order_confirmation_email(order):
    print("order_confirmation_email method called")
    subject = 'Order Confirmation'
    html_message = render_to_string(
        'email/order_confirmation.html', {'order': order})
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    to = order.customer.user.email

    try:
        print(f"Attempting to send email to {to}")
        send_mail(subject, plain_message, from_email,
                  [to], html_message=html_message)
        print(f"Email sent successfully to {to}")
    except BadHeaderError:
        print(f"Invalid header found while sending email to {to}")
    except Exception as e:
        print(f"Failed to send email to {to}: {str(e)}")


def my_orders(request):
    user = request.user

    if not user.is_authenticated:

        pass

    # Get the customer associated with the user
    customer = get_object_or_404(Customer, user=user)

    # Get the orders for the customer
    orders = Order.objects.filter(
        customer=customer).prefetch_related('items', 'items__product')
    # Calculate total price for each order
    for order in orders:
        items = order.items.all()
        order.total_price = sum(
            item.unit_price * item.quantity for item in items)

    return render(request, 'store/my_orders.html', {'orders': orders})


def search_suggestions(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(title__icontains=query)[
            :5]  # Limit to 5 suggestions
    else:
        products = []

    suggestions = []
    for product in products:
        first_image = product.images.first()
        image_url = first_image.image.url if first_image else None
        suggestions.append({
            'id': product.id,
            'title': product.title,
            'image_url': image_url
        })
    return JsonResponse(suggestions, safe=False)


def search(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(title__icontains=query)
    else:
        products = Product.objects.all()
    return render(request, 'store/search_results.html', {'products': products})
