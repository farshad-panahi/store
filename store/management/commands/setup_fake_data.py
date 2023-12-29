# setup_test_data.py
import random
from faker import Faker
from datetime import datetime, timedelta
import factory
from factory.fuzzy import FuzzyDateTime

from django.db import transaction
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from django.utils.timezone import get_current_timezone
from config import settings

from store.models import Address, Cart, CartItem, Category, Comment, Order, OrderItem, Product, Discount, Customer
from store.factories import (
	CartFactory,
	CategoryFactory,
	CommentFactory,
	OrderItemFactory,
	ProductFactory,
	DiscountFactory,
	CustomerFactory,
	AddressFactory,
	OrderFactory,
	CartItemFactory,
)

faker = Faker()

list_of_models = [CartItem, Cart, OrderItem, Order, Product, Category, Comment, Discount, Address, Customer]

NUM_CATEGORIES = 100
NUM_DISCOUNTS = 10
NUM_PRODUCTS = 1000
NUM_CUSTOMERS = 100
NUM_ORDERS = 30
NUM_CARTS = 100


class Command(BaseCommand):
	help = "Generates fake data"

	@transaction.atomic
	def handle(self, *args, **kwargs):
		self.stdout.write("Deleting old data...")
		models = list_of_models
		for m in models:
			m.objects.all().delete()

		self.stdout.write("Creating new data...\n")

		tz = timezone.get_current_timezone()

		# Categories data
		print(f"Adding {NUM_CATEGORIES} categories...", end='')
		all_categories = [CategoryFactory(top_product=None) for _ in range(NUM_CATEGORIES)]
		print('DONE')

		# Discounts data
		print(f"Adding {NUM_DISCOUNTS} discounts...", end='')
		all_discounts = [DiscountFactory() for _ in range(NUM_DISCOUNTS)]
		print('DONE')

		# Products data
		print(f"Adding {NUM_PRODUCTS} product...", end='')
		all_products = list()
		for _ in range(NUM_PRODUCTS):
			new_product = ProductFactory(category_id=random.choice(all_categories).id)
			new_product.datetime_created = datetime(random.randrange(2019, 2023), random.randint(1, 12),
													random.randint(1, 12), tzinfo=timezone.timezone.utc)
			new_product.datetime_modified = new_product.datetime_created + timedelta(hours=random.randint(1, 500))
			new_product.save()
			all_products.append(new_product)
		print('DONE')

		# Customers data
		print(f"Adding {NUM_CUSTOMERS} customers...", end='')
		all_customers = [(CustomerFactory() if (random.random() > 0.3) else CustomerFactory(birth_date=None)) for _ in
						 range(NUM_CUSTOMERS)]
		print('DONE')

		# Addresses data
		print(f"Adding customers addresses...", end='')
		all_addresses = [
			AddressFactory(customer_id=customer.id) for customer in all_customers
		]
		print('DONE')

		# Orders data
		print(f"Adding {NUM_ORDERS} orders...", end='')
		all_orders = [OrderFactory(
			customer_id=random.choice(all_customers).id
		) for _ in range(NUM_ORDERS)]
		for order in all_orders:
			order.datetime_created = datetime(random.randrange(2019, 2023), random.randint(1, 12),
											  random.randint(1, 12), tzinfo=timezone.timezone.utc)
			order.save()
		print('DONE')

		# OrderItems data
		print(f"Adding order items...", end='')
		all_order_items = list()
		for order in all_orders:
			products = random.sample(all_products, random.randint(1, 10))
			for product in products:
				order_item = OrderItemFactory(
					order_id=order.id,
					product_id=product.id,
					unit_price=product.unit_price,
				)
				all_order_items.append(order_item)
		print('DONE')

		# Comments data
		print(f"Adding product comments...", end='')
		for product in all_products:
			for _ in range(random.randint(1, 5)):
				comment = CommentFactory(product_id=product.id)
				comment.datetime_created = datetime(random.randrange(2019, 2023), random.randint(1, 12),
													random.randint(1, 12), tzinfo=timezone.timezone.utc)
				comment.save()
		print('DONE')

		# Carts data
		print(f"Adding {NUM_CARTS} carts...", end='')
		all_carts = [CartFactory() for _ in range(NUM_CARTS)]
		print('DONE')

		# CartItems data
		print(f"Adding cart items...", end='')
		all_cart_items = list()
		for cart in all_carts:
			products = random.sample(all_products, random.randint(1, 10))
			for product in products:
				cart_item = CartItemFactory(
					cart_id=cart.id,
					product_id=product.id,
				)
				all_cart_items.append(cart_item)
		print('DONE')