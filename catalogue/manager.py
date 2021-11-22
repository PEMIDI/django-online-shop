from django.db import models


class ProductQuerySet(models.QuerySet):
    def activates(self):
        return self.filter(is_available=True)

    def deactivates(self):
        return self.exclude(is_available=True)

    def join(self):
        return self.select_related('category', 'brand')


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def activates(self):
        return self.get_queryset().activates()

    def deactivates(self):
        return self.get_queryset().deactivates()

    def join(self):
        return self.get_queryset().join()
