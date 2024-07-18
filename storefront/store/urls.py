from django.urls import path
from rest_framework_nested import routers
from . import views

app_name = 'store'


router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet)
router.register('carts', views.CartViewSet)
router.register('customers', views.CustomerViewSet, basename='customers')
router.register('orders', views.OrderViewSet, basename='orders')

products_router = routers.NestedDefaultRouter(
    router, 'products', lookup='product')
products_router.register('reviews', views.ReviewViewSet,
                         basename='product-reviews')
products_router.register(
    'images', views.ProductImageViewSet, basename='product-images')
orders_router = routers.NestedDefaultRouter(router, 'orders', lookup='order')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

# urlpatterns =[
#     path('products_page', views.\)
# ]

# URLConf
urlpatterns = router.urls + products_router.urls + carts_router.urls

urlpatterns += [

    path('products/products_page/',
         views.ProductViewSet.as_view({'get': 'products_page'}), name='products_page'),
    path('order_form', views.order_form_view, name='order_form'),
    path('order_success', views.order_success_page, name='order_success'),
    path('my_orders', views.my_orders, name='my_orders'),
    path('post_order', views.post_order, name='post_order'),
    path('search/', views.search, name='search'),
    path('search/suggestions/', views.search_suggestions,
         name='search_suggestions'),
]
