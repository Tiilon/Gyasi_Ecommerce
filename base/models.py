from django.db import models
import uuid


#with created by field
class BaseModel(models.Model):
    uid = models.UUIDField(editable=False , default=uuid.uuid4, unique=True)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now= True)
    updated_at = models.DateTimeField(auto_now_add= True)

    class Meta:
        abstract = True 