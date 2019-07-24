from django.db import models
from django.utils.translation import gettext_lazy as _


class AttributeName(models.Model):
    nazev = models.CharField(max_length=120, verbose_name=_('Name'))
    kod = models.CharField(max_length=120, null=True, blank=True, verbose_name=_('Code'))
    zobrazit = models.BooleanField(default=False, verbose_name=_('Show it'))

    def __str__(self):
        return self.nazev


class AttributeValue(models.Model):
    hodnota = models.CharField(max_length=120, verbose_name=_('Value'))

    def __str__(self):
        return self.hodnota


class Attribute(models.Model):
    nazev_atributu_id = models.ForeignKey(AttributeName, on_delete=models.CASCADE, verbose_name=_('Attribute name'))
    hodnota_atributu_id = models.ForeignKey(AttributeValue, on_delete=models.CASCADE, verbose_name=_('Attribute value'))


class Product(models.Model):
    CURRENCIES = [
        ("CZK", "CZK"),
        ("EUR", "EUR"),
    ]

    nazev = models.CharField(max_length=180, verbose_name=_('Name'))
    description = models.TextField(verbose_name=_('Description'))
    cena = models.DecimalField(max_digits=9, decimal_places=2, verbose_name=_('Price'))
    mena = models.CharField(max_length=3, choices=CURRENCIES, default=CURRENCIES[0][0], verbose_name=_('Currency'))
    published_on = models.DateTimeField(null=True, blank=True, verbose_name=_('Published_on'))
    is_published = models.BooleanField(default=False, verbose_name=_('Is published?'))

    def __str__(self):
        return self.nazev


class ProductAttributes(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, verbose_name=_('Attribute'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('Product'))


class Image(models.Model):
    nazev = models.CharField(max_length=180, null=True, blank=True, verbose_name=_('Name'))
    obrazek = models.URLField(verbose_name=_('Source URL'))


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('Product'))
    obrazek_id = models.ForeignKey(Image, on_delete=models.CASCADE, verbose_name=_('Image'))
    nazev = models.CharField(max_length=180, verbose_name=_('Name'))


class Catalog(models.Model):
    nazev = models.CharField(max_length=180, verbose_name=_('Name'))
    obrazek_id = models.ForeignKey(Image, on_delete=models.CASCADE, verbose_name=_('Image'))
    products_ids = models.ManyToManyField(Product, related_name='catalogs', verbose_name=_('Products'))
    attributes_ids = models.ManyToManyField(Attribute, related_name='+', verbose_name=_('Attributes'))

    def __str__(self):
        return self.nazev
