from django.db import models

# Create your models here.

class Flight(models.Model):
    # This is an attempt to create a sql database template
    gate = models.CharField(max_length=10)
    flight_number = models.CharField(max_length=10)
    scheduled = models.DateTimeField()
    actual = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.gate,} - {self.flight_number}"


class SearchQuery(models.Model):
    query = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)            # adds a timestamp