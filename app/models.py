from django.db import models
from django.contrib.auth.models import User  


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategoriya nomi")

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Kategoriyasi")
    name = models.CharField(max_length=255, verbose_name="Mahsulot nomi")
    description = models.TextField(blank=True, null=True, verbose_name="Tavsifi")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Narxi")
    

    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Mahsulot rasmi")
    
    stock = models.IntegerField(default=0, verbose_name="Ombordagi soni")
    is_available = models.BooleanField(default=True, verbose_name="Sotuvda bor")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")

    def __str__(self):
        return self.name
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE) # <-- Qo'shtirnoq olib tashlandi (toza chiqishi uchun)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(verbose_name="Sharh matni")
    rating = models.IntegerField(default=5, verbose_name="Baholash (1-5)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating} ⭐)"