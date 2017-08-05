from django.contrib import admin

# Register your models here.
from adminapp.models import Category,SubCategory,State,City,Section

admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(State)
admin.site.register(City)
admin.site.register(Section)
