from django.db import models


class ApplicationHistory(models.Model):
    """
    A record of every application attempt that comes through the API,
    whether the email actually went out or not. This is what lets you
    look back later and see what was sent, to whom, when, and whether
    it succeeded.
    """

    STATUS_CHOICES = [
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]

    recipient_email = models.EmailField()
    role = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-sent_at"]

    def __str__(self):
        return f"{self.role} -> {self.recipient_email} ({self.status})"
