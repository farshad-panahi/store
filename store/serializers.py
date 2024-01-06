from django.utils.text import slugify
from rest_framework import serializers

from .models import Product, Category, Comment, Cart, CartItem


class CategorySerializer(serializers.ModelSerializer):
	amount = serializers.SerializerMethodField()

	class Meta:
		model = Category
		fields = ('id', 'title', 'description', 'amount')

	@staticmethod
	def get_amount(category):
		return category.products.count()

	@staticmethod
	def title_validate(validated_data):
		if not len(validated_data["title"]) > 3:
			raise serializers.ValidationError('title length must be at least 3 characters')
		return validated_data


# ModelSerializer for saving objects in methods


class ProductSerializer(serializers.ModelSerializer):
	title = serializers.CharField(max_length=255, source='name')
	unit_price = serializers.DecimalField(max_digits=6, decimal_places=2)

	class Meta:
		model = Product
		fields = ('title', 'unit_price', 'category', 'inventory', 'description')

	def create(self, validated_data):
		new_product = Product(**validated_data)
		new_product.slug = slugify(new_product.name)
		new_product.save()
		return new_product


class CommentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Comment
		fields = ('id', 'name', 'body',)

	def create(self, validated_data):
		print(self.context)
		product_id = self.context['product_pk']
		return Comment.objects.create(
			product_id=product_id,
			**validated_data
		)


class CartProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		fields = ['id', 'name', 'unit_price']


class UpdateCartItemSerializer(serializers.ModelSerializer):
	class Meta:
		model = CartItem
		fields = ['quantity']


class AddCartItemSerializer(serializers.ModelSerializer):
	class Meta:
		model = CartItem
		fields = ['id', 'product', 'quantity']

	def create(self, validated_data):
		cart_id = self.context['cart_pk']

		product = validated_data.get('product')
		quantity = validated_data.get('quantity')

		try:
			cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product.id)
			cart_item.quantity += quantity
			cart_item.save()
		except CartItem.DoesNotExist:
			cart_item = CartItem.objects.create(cart_id=cart_id, **validated_data)

		self.instance = cart_item
		return cart_item

class CartItemSerializer(serializers.ModelSerializer):
	product = CartProductSerializer()
	item_total = serializers.SerializerMethodField()

	class Meta:
		model = CartItem
		fields = ('id', 'product', 'quantity', 'item_total')

	@staticmethod
	def get_item_total(cart_item: CartItem):
		return cart_item.quantity * cart_item.product.unit_price


class CartSerializer(serializers.ModelSerializer):
	items = CartItemSerializer(many=True, read_only=True)
	total_price = serializers.SerializerMethodField()

	class Meta:
		model = Cart
		fields = ('id', 'items', 'total_price',)
		read_only_fields = ['id']

	@staticmethod
	def get_total_price(cart: Cart):
		return sum([item.quantity * item.product.unit_price for item in cart.items.all()])
