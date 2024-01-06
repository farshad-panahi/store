from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.response import Response
from .filters import ProductFilterSet
from .serializers import ProductSerializer, CategorySerializer, CommentSerializer, CartSerializer, CartItemSerializer, \
	AddCartItemSerializer, UpdateCartItemSerializer
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from .paginations import DefaultPageination

from .models import Product, Category, Comment, Cart, CartItem


class ProductViewSet(ModelViewSet):
	queryset = Product.objects.all()
	serializer_class = ProductSerializer
	filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter, ]
	search_fields = ['name', 'category__title', ]
	ordering_fields = ['name', 'unit_price', 'inventory']
	# filterset_fields = ['category_id']
	filterset_class = ProductFilterSet
	pagination_class = DefaultPageination

	def get_queryset(self):
		queryset = Product.objects.all()
		category_id_parameter = self.request.query_params.get('category_id')
		if category_id_parameter is not None:
			queryset = queryset.filter(category_id=category_id_parameter)
		return queryset

	def get_serializer_context(self):
		return {'request': self.request}

	def destroy(self, request, pk):
		product = get_object_or_404(Product.objects.select_related('category'), pk=pk)
		if product.order_items.count() > 0:
			return Response({
				"Error": "This product is in some order items, first delete them all."
			})
		product.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(ModelViewSet):
	serializer_class = CategorySerializer
	queryset = Category.objects.prefetch_related('products').all()

	def destroy(self, request, pk, ):
		category = get_object_or_404(Category.objects.prefetch_related('products'), pk=pk)
		if category.products.count() > 0:
			return Response(
				{'Errors': 'This category has has products in it, first delete those'}
			)
		category.delete()
		return Response('Deleted category', status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(ModelViewSet):
	serializer_class = CommentSerializer

	def get_queryset(self):
		product_pk = self.kwargs['product_pk']
		return Comment.objects.filter(product_id=product_pk).all()

	def get_serializer_context(self):
		return {
			'product_pk': self.kwargs['product_pk']
		}


class CartItemViewSet(ModelViewSet):
	http_method_names = ['get', 'post', 'patch', 'delete']
	def get_queryset(self):
		cart_pk = self.kwargs['cart_pk']
		return CartItem.objects.filter(cart_id=cart_pk).all()

	def get_serializer_class(self):
		if self.request.method == 'POST':
			return AddCartItemSerializer

		elif self.request.method == 'PATCH':
			return UpdateCartItemSerializer

		return CartItemSerializer

	def get_serializer_context(self):
		return {'cart_pk': self.kwargs['cart_pk']}


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
	serializer_class = CartSerializer
	queryset = Cart.objects.prefetch_related('items__product').all()

	lookup_value_regex = '[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}'
