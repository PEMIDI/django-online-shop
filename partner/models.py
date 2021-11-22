from django.db import models

from catalogue.models import Product


class Partner(models.Model):
    name = models.CharField(max_length=48)

    def __str__(self):
        return self.name


class PartnerStock(models.Model):
    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
        related_name='partners'
    )
    partner = models.ForeignKey(
        to=Partner,
        on_delete=models.CASCADE,
        related_name='products'
    )

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.product} - {self.partner} - {self.price}'
