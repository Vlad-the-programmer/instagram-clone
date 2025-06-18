from django.contrib import admin
from .models import UserFollowing


class CustomUserFollowingAdmin(admin.ModelAdmin):
    model = UserFollowing
    list_display = ['user_id',
                    'following_user_id',
                    'created_at',
                    ]
    list_filter = ()
    search_fields = ['user_id', 'following_user_id']
    
admin.site.register(UserFollowing, CustomUserFollowingAdmin)




