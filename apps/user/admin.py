from django.contrib import admin

from user.models import User, Address

admin.site.register([User, Address])
