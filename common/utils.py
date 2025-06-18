from django.utils.text import slugify
from django.db import models
from typing import Union

def set_slug(obj: models.Model, modelOrManager: Union[models.Model,models.Manager]) -> None:
    existingObj = modelOrManager.filter(slug=obj.slug)
        
    if existingObj.exists():
        obj.slug = slugify(obj.title + "-" + obj.pkid) 