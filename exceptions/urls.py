from django.urls import path
from django.views.generic.base import TemplateView

from . import views

app_name = 'exceptions'

urlpatterns = [
    path('403_access_forbidden', TemplateView.as_view(
                                        template_name="exceptions/403_access_forbidden.html"),
                                        name='403_access_forbidden'),

]
