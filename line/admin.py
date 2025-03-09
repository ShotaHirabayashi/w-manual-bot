from django.contrib import admin

# Register your models here.
from .models import Customer

# line_idはReadOnlyにする
class CustomerAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    readonly_fields = ('line_id','name','updated_at','created_at')

admin.site.register(Customer, CustomerAdmin)

