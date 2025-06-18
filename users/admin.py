from django.contrib import admin
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
# from .models import Profile

Profile = get_user_model()


class CustomUserAdmin(admin.ModelAdmin):
    model = Profile
    list_display = ['pkid', 
                    'id',
                    'email',
                    'username',
                    'featured_img',
                    'first_name',
                    'last_name',
                    'country',
                    'gender',
                    'is_superuser',
                    'is_active',
                    'is_staff',
                    'date_joined',
                    'last_login',
                    ]
    list_filter = ()
    search_fields = ['email', 'username']
admin.site.register(Profile, CustomUserAdmin)


class SiteAdmin(admin.ModelAdmin):
    model = Site
    list_display = ['id', 'domain']

admin.site.unregister(Site)
admin.site.register(Site, SiteAdmin)


