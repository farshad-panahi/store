from django.utils.text import slugify
from rest_framework import serializers

from .models import Product, Category, Comment


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
		fields = ('id', 'name', 'body', )

	def create(self, validated_data):
		print(self.context)
		product_id = self.context['product_pk']
		return Comment.objects.create(
			product_id=product_id,
			**validated_data
		)

