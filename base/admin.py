from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


# Register your models here.
from .models import *


class MyUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("photo", 'slug', 'about')}),
    )
    prepopulated_fields = {'slug': ['username',]}


admin.site.register(User, MyUserAdmin)
admin.site.register(Topic)
admin.site.register(Post)
admin.site.register(Follow)
