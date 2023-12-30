from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from django.urls import reverse
from django.utils.html import urlencode

from . import models


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ['title', 'description', 'top_product']


class InventoryFilter(admin.SimpleListFilter):
	LESS_THAN_3 = '<3'
	BETWEEN_3_AND_10 = '3<=10'
	MORE_THAN_10 = '>10'

	title = 'Critical needs of products'
	parameter_name = 'inventory'

	def lookups(self, request, model_admin):
		return [
			(InventoryFilter.LESS_THAN_3, 'URGENT NEEDS'),
			(InventoryFilter.BETWEEN_3_AND_10, 'NEEDS ATTENTION'),
			(InventoryFilter.MORE_THAN_10, 'NO NEED YET'),
		]

	def queryset(self, request, queryset):
		if self.value() == InventoryFilter.LESS_THAN_3:
			return queryset.filter(inventory__lt=3)
		if self.value() == InventoryFilter.BETWEEN_3_AND_10:
			return queryset.filter(inventory__range=(4, 10))
		if self.value() == InventoryFilter.MORE_THAN_10:
			return queryset.filter(inventory__gt=10)


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
	list_display = ['first_name', 'last_name', 'email']
	list_per_page = 20
	ordering = ('first_name', 'last_name', 'email')
	search_fields = ['first_name', 'last_name', ]


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ['id', 'name', 'inventory', 'unit_price', 'amount_status', 'product_category', 'number_of_comments']
	ordering = ('id',)
	list_per_page = 20
	list_editable = ['unit_price']
	list_select_related = ['category', ]
	list_filter = ['date_created', InventoryFilter]
	actions = ['clear_inventory']
	list_display_links = ['id', 'name']
	search_fields = ['name']
	prepopulated_fields = {
		'slug': ['name', 'description', 'unit_price'],
	}

	def get_queryset(self, request):
		return super() \
			.get_queryset(request) \
			.prefetch_related('comments') \
			.annotate(
			comments_count=Count('comments')
		)

	@staticmethod
	@admin.display(ordering='category__title')
	def product_category(product: models.Product):
		return product.category.title

	@staticmethod
	@admin.display(description='# comments related', ordering='comments_count')
	def number_of_comments(product: models.Product):
		url = (
				reverse('admin:store_comment_changelist')
				+ "?"
				+ urlencode({'product__id': product.id})
		)
		return format_html('<a href="{}">{}</a>', url, product.comments.count())

	@staticmethod
	@admin.display(ordering='inventory')
	def amount_status(product: models.Product):
		if product.inventory < 10:
			return 'low amount'
		elif product.inventory > 50:
			return 'high amount'
		return 'medium amount'

	@admin.action(description='clear inventory')
	def clear_inventory(self, request, queryset):
		update_count_of_inventory = queryset.update(inventory=0)
		self.message_user(
			request,
			F"{update_count_of_inventory} items' inventory cleared to 0" \
				if not update_count_of_inventory == 1 \
				else F"{update_count_of_inventory} item's inventory cleared to 0"
		)


class OrderItemInline(admin.TabularInline):
	model = models.OrderItem
	fields = ['product', 'order', 'quantity', 'unit_price']
	extra = 1
	min_num = 1
	max_num = 100


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ['id', 'customer', 'status', 'datetime_created', 'number_of_items']
	list_editable = ['status']
	ordering = ('-datetime_created',)
	inlines = [OrderItemInline, ]
	list_display_links = ['customer', ]
	autocomplete_fields = ['customer']

	def get_queryset(self, request):
		return super() \
			.get_queryset(request) \
			.select_related('customer', ) \
			.prefetch_related('items', ) \
			.annotate(
			items_count=Count('items')
		)

	@staticmethod
	@admin.display(ordering='items_count', description='# items')
	def number_of_items(order):
		return order.items_count


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
	list_display = ['id', 'product', 'status', 'datetime_created', 'body']
	list_editable = ['status']
	list_per_page = 10
	autocomplete_fields = ['product', ]
	list_display_links = ['id', 'product']

