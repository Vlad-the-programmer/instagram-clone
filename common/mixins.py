import logging

from django.http import HttpResponse
# Auth
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy

logger = logging.getLogger(__name__)


class InvalidFormMixin:
    """Custom form invalid mixin that adds messages"""
    def form_invalid(self, form) -> HttpResponse:
        """Handle invalid form submission."""
        messages.error(
            self.request,
            'Please correct the errors below.'
        )

        # If form is invalid, show errors
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field.title()}: {error}")

        return super().form_invalid(form)

class HandleNotFoundObjectMixin:
    def dispatch(self, request, *args, **kwargs):
        # Check if the object exists before proceeding
        self.object = self.get_object()
        if self.object is None:
            return redirect(reverse_lazy("exceptions:404_not_found"))
        return super().dispatch(request, *args, **kwargs)
