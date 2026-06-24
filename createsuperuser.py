import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oo.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
# 'admin' degan login va 'admin123' parolli admin yaratadi
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser muvaffaqiyatli yaratildi!")
else:
    print("Superuser allaqachon bor.")
