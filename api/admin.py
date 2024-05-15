from django.contrib import admin
from .models import user , review , picture , product , CustomUserManager , reservation
# Register your models here.


admin.site.register(user)
admin.site.register(review)
admin.site.register(picture)
admin.site.register(product)
admin.site.register(reservation)

