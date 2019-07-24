from django.db import models
from django.utils.translation import gettext_lazy as _


class UpdateMixin:
    def update(self, **kwargs):
        if self._state.adding:
            raise self.DoesNotExist
        dirty = dirty_m2m = False
        for field, value in kwargs.items():
            if getattr(self, field) != value:
                easy = True
                if type(value) is list:
                    fld = self._meta.get_field(field)
                    if isinstance(fld, models.fields.related.ManyToManyField):  # covers m2m, but probably not working for explicit through=.. !!
                        easy = False
                        manager = getattr(self, fld.attname)
                        oldval = manager.all()
                        if set(oldval) == set(value):
                            continue   # no change required
                        manager.set(value, clear=True)
                        dirty = dirty_m2m = True
                if easy:  # covers FK + non-relational fields
                    setattr(self, field, value)
                    dirty = True
        if dirty:
            if dirty_m2m:
                self.save()
            else:
                self.save(update_fields=kwargs.keys())
            return True  # really updated
        return False

        '''
        ManyToManyField:
        https://stackoverflow.com/questions/32553100/how-to-update-m2m-field-in-django
        https://stackoverflow.com/questions/2849108/how-to-check-the-type-of-a-many-to-many-field-in-django

        today_ref_pk = [1,2,3]
        u = MyUser.objects.get(pk=1)
        u.today_ref_viewed_ips.clear()
        u.today_ref_viewed_ips.add(*today_ref_pk)

        # dj >= 1.11
        today_ref_objs = [obj1, obj2, obj3]
        u = MyUser.objects.get(pk=1)
        u.today_ref_viewed_ips.set(today_ref_objs, clear=True)
        '''


class AttributeName(models.Model, UpdateMixin):
    nazev = models.CharField(max_length=120, verbose_name=_('Name'))
    kod = models.CharField(max_length=120, null=True, blank=True, verbose_name=_('Code'))
    zobrazit = models.BooleanField(default=False, verbose_name=_('Show it'))

    def __str__(self):
        return self.nazev


class AttributeValue(models.Model, UpdateMixin):
    hodnota = models.CharField(max_length=120, verbose_name=_('Value'))

    def __str__(self):
        return self.hodnota


class Attribute(models.Model, UpdateMixin):
    nazev_atributu_id = models.ForeignKey(AttributeName, on_delete=models.CASCADE, verbose_name=_('Attribute name'))
    hodnota_atributu_id = models.ForeignKey(AttributeValue, on_delete=models.CASCADE, verbose_name=_('Attribute value'))


class Product(models.Model, UpdateMixin):
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


class ProductAttributes(models.Model, UpdateMixin):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, verbose_name=_('Attribute'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('Product'))


class Image(models.Model, UpdateMixin):
    nazev = models.CharField(max_length=180, null=True, blank=True, verbose_name=_('Name'))
    obrazek = models.URLField(verbose_name=_('Source URL'))


class ProductImage(models.Model, UpdateMixin):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('Product'))
    obrazek_id = models.ForeignKey(Image, on_delete=models.CASCADE, verbose_name=_('Image'))
    nazev = models.CharField(max_length=180, verbose_name=_('Name'))


class Catalog(models.Model, UpdateMixin):
    nazev = models.CharField(max_length=180, verbose_name=_('Name'))
    obrazek_id = models.ForeignKey(Image, on_delete=models.CASCADE, verbose_name=_('Image'))
    products_ids = models.ManyToManyField(Product, related_name='catalogs', verbose_name=_('Products'))
    attributes_ids = models.ManyToManyField(Attribute, related_name='+', verbose_name=_('Attributes'))

    def __str__(self):
        return self.nazev
