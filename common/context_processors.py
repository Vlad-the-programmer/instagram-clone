from users.models import Profile

def template_context_processor(request, *args, **kwargs):
    user = request.user
    print('Current user: ', user)
    if user.is_authenticated:
        profile = Profile.objects.filter(email=user.email).first()
        print('Context proc Profile: ', profile)
        return {'user': user, 'profile': profile}
    else:
        return {'user': '', 'profile': ''}