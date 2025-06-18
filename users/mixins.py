
# Auth
from django.contrib.auth import get_user_model
Profile = get_user_model()


class GetProfileObjectMixin():
    def get_object(self):
        pk_ = self.kwargs.get('pk', '')
        
        try:
            profile = Profile.objects.get(id=pk_)
        except Profile.DoesNotExist:
            profile = None
        return profile
    