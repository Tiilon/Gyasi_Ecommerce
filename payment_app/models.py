from django.db import models
import secrets
from .paystack import PayStack #pyright:ignore

class Payment(models.Model):
    amount = models.PositiveIntegerField()
    reference = models.CharField(max_length=200)
    email = models.EmailField()
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('-created_at',)
        
    def __str__(self):
        return f"Payment: {self.amount}"
    
    def save(self, *args, **kwargs) -> None:
        while not self.reference:
            ref = secrets.token_urlsafe(50)
            object_with_similar_reference = Payment.objects.filter(reference=ref)
            if not object_with_similar_reference:
                self.reference = ref
        super().save(*args, **kwargs)
        
    def amount_value(self) -> int:
        return self.amount * 100
    
    def verify_payment(self):
        paystack = PayStack()
        status, result = paystack.verify_payment(self.reference, self.amount)
        if status:
            if result['amount'] / 100 == self.amount:
                self.verified = True
            self.save()
            return bool(self.verified)
