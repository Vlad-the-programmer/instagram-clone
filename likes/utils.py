from .models import Like, Dislike

def get_user_like_and_delete(user, post) -> None:
    like = Like.objects.filter(author=user, post=post).first()
    
    if like is not None:
        like.delete()
        
        
def get_user_dislike_and_delete(user, post) -> None:
    dislike = Dislike.objects.filter(author=user, post=post).first()
    
    if dislike is not None:
        dislike.delete()