# from django.urls import path, include
from . import views
from rest_framework_nested import routers

router = routers.DefaultRouter()

router.register('products', views.ProductViewSet, basename='product')
router.register('categories', views.CategoryViewSet, basename='category')
router.register('carts', views.CartViewSet)
product_router = routers.NestedDefaultRouter(
	router,
	'products',
	lookup='product',
)
product_router.register('comments', views.CommentViewSet, basename='product-comments')

cart_items_router = routers.NestedDefaultRouter(
	router,
	'carts',
	lookup='cart'
)
cart_items_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = router.urls + product_router.urls + cart_items_router.urls
