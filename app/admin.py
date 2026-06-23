from django.contrib import admin
from .models import Category, Product, Review, Order, OrderItem

# Mahsulot ichida buyurtma elementlarini chiroyli ko'rsatish uchun
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Admin panel jadvalida ko'rinadigan ustunlar
    list_display = ['id', 'user', 'phone', 'total_price', 'is_paid', 'created_at']
    # O'ng tomonda filtr qo'yish paneli
    list_filter = ['is_paid', 'created_at']
    # Qidiruv tizimi
    search_fields = ['user__username', 'phone', 'address']
    # Buyurtma ichiga kirganda mahsulotlarini ham pastida ko'rsatish
    inlines = [OrderItemInline]

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'product__name', 'comment']

# Agar avval ro'yxatdan o'tmagan bo'lsa, bularni ham qo'shib qo'yamiz
try:
    admin.site.register(Category)
    admin.site.register(Product)
except admin.sites.AlreadyRegistered:
    pass