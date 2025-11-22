from django.contrib import admin

# Register your models here.
from .models import Statements,CategoryList,Categories

admin.site.register(Statements)
admin.site.register(Categories)
admin.site.register(CategoryList)
