from django.shortcuts import render, get_object_or_404, redirect
from .models import Product,Order,OrderItem,Category
from django.contrib import messages  # <-- MANA SHU QATORNI QO'SHING
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required

# O'sha xato turgan "from types import" degan qatorni butunlay o'chirib tashlang!
# 1. Asosiy sahifa funksiyasi
# app/views.py faylidagi home funksiyasi

def home(request):
    # Mavjud barcha mahsulotlarni olish
    products = Product.objects.all()
    
    # 1. Qidiruv logikasi (agar bor bo'lsa)
    query = request.GET.get('search')
    if query:
        products = products.filter(name__icontains=query)
        
    # 2. Kategoriya bo'yicha filtr (agar bor bo'lsa)
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
        
    # 3. YANGI: Saralash (Sorting) logikasi
    sort_by = request.GET.get('sort', '') # default holatda bo'sh bo'ladi
    if sort_by == 'price_asc':
        products = products.order_by('price')       # Arzonidan qimmatiga
    elif sort_by == 'price_desc':
        products = products.order_by('-price')      # Qimmatidan arzoniga
    elif sort_by == 'newest':
        products = products.order_by('-id')         # Yangi qo'shilganlar (ID bo'yicha teskari)

    # Boshqa kerakli o'zgaruvchilar (kategoriyalar ro'yxati, savat soni va h.k.)
    categories = Category.objects.all()
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())
    
    return render(request, 'home.html', {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'current_sort': sort_by, # joriy saralash turini andozaga uzatamiz
        'cart_count': cart_count
    })
# 2. Savatga qo'shish funksiyasi
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        cart[product_id_str] += 1
    else:
        cart[product_id_str] = 1
        
    request.session['cart'] = cart
    request.session.modified = True
    
    # Xabar matnini oddiy qoldiramiz, lekin extra_tags yordamida mahsulot ID sini beramiz
    messages.success(request, "✨ Muvaffaqiyatli qo'shildi!", extra_tags=str(product_id))
    
    return redirect('home')

# 3. Savat sahifasining o'zi
def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            item_total = product.price * quantity
            total_price += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total
            })
        except Product.DoesNotExist:
            continue
            
    return render(request, 'cart_detail.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })  

# 4. Savatdan 1 ta mahsulotni ayirish (kamaytirish)
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        if cart[product_id_str] > 1:
            cart[product_id_str] -= 1
        else:
            cart.pop(product_id_str) # Agar 1 ta bo'lsa, nolgacha tushirmasdan o'chirib tashlaydi
            
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart_detail')

# 5. Mahsulotni savatdan butunlay o'chirish
def delete_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        cart.pop(product_id_str)
        
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart_detail')

# 1. Ro'yxatdan o'tish
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

# 2. Tizimga kirish
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# 3. Tizimdan chiqish
def logout_view(request):
    auth_logout(request)
    return redirect('home')

# 4. Profil sahifasi (faqat kirganlar ko'ra oladi)
@login_required(login_url='login')
# app/views.py fayli ichida

@login_required(login_url='login')
def profile_view(request):
    # Foydalanuvchiga tegishli barcha buyurtmalarni eng yangisidan boshlab olamiz
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'profile.html', {'orders': orders})
@login_required(login_url='login')
def checkout_view(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('home')

    # Savatdagi mahsulotlarni va umumiy narxni hisoblash
    cart_items = []
    total_price = 0
    for product_id, quantity in cart.items():
        product = Product.objects.get(id=int(product_id))
        total_price += product.price * quantity
        cart_items.append({'product': product, 'quantity': quantity})

    if request.method == 'POST':
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        
        # 1. Buyurtmani yaratish
        order = Order.objects.create(
            user=request.user,
            address=address,
            phone=phone,
            total_price=total_price,
            is_paid=True # Bu yerda to'lov muvaffaqiyatli deb hisoblaymiz
        )
        
        # 2. Buyurtma ichidagi mahsulotlarni saqlash
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['product'].price
            )
            # Ombordagi sonini kamaytirish
            item['product'].stock -= item['quantity']
            item['product'].save()

        # 3. Savatchani tozalash
        request.session['cart'] = {}
        messages.success(request, "Xaridingiz uchun rahmat! Buyurtma qabul qilindi.")
        return redirect('home')

    return render(request, 'checkout.html', {'total_price': total_price})
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Review # Review modelini import qilishni unutmang
from django.contrib import messages

def product_detail_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Agar foydalanuvchi sharh yozib, "Yuborish"ni bossa (POST so'rovi)
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "Sharh qoldirish uchun tizimga kiring!")
            return redirect('login')
            
        comment_text = request.POST.get('comment')
        rating_value = request.POST.get('rating')
        
        if comment_text and rating_value:
            Review.objects.create(
                product=product,
                user=request.user,
                comment=comment_text,
                rating=int(rating_value)
            )
            messages.success(request, "Sharhingiz muvaffaqiyatli qo'shildi!")
            return redirect('product_detail', product_id=product.id)

    # Mahsulotga tegishli barcha sharhlarni bazadan olish
    reviews = product.reviews.all().order_by('-created_at')
    
    # Savatdagi son
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())
    
    return render(request, 'product_detail.html', {
        'product': product,
        'reviews': reviews,
        'cart_count': cart_count
    })
