from rest_framework import serializers

from . import models


class AbstractSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField()
    list_fields = ['id']

    def __init__(self, *args, **kwargs):
        as_list = kwargs.pop('as_list', False)
        super().__init__(*args, **kwargs)
        if as_list:
            # self.fields = self.list_fields : not possible to do, because self.fields has more info inside
            exclude = []
            for fld in self.fields:
                if fld not in self.list_fields:
                    exclude.append(fld)  # to be sure, we avoid deletion during the cycle over same dict ..
            for fld in exclude:          # .. and do it in separate step
                del self.fields[fld]


class AttributeNameSerializer(AbstractSerializer):
    class Meta:
        model = models.AttributeName
        fields = ['id', 'nazev', 'kod', 'zobrazit']


class AttributeValueSerializer(AbstractSerializer):
    class Meta:
        model = models.AttributeValue
        fields = ['id', 'hodnota']


class AttributeSerializer(AbstractSerializer):
    class Meta:
        model = models.Attribute
        fields = ['id', 'nazev_atributu_id', 'hodnota_atributu_id']


class ProductSerializer(AbstractSerializer):
    class Meta:
        model = models.Product
        fields = ['id', 'nazev', 'description', 'cena', 'mena', 'published_on', 'is_published']


class ProductAttributesSerializer(AbstractSerializer):
    class Meta:
        model = models.ProductAttributes
        fields = ['id', 'attribute', 'product']


class ImageSerializer(AbstractSerializer):
    class Meta:
        model = models.Image
        fields = ['id', 'nazev', 'obrazek']


class ProductImageSerializer(AbstractSerializer):
    class Meta:
        model = models.ProductImage
        fields = ['id', 'product', 'obrazek_id', 'nazev']


class CatalogSerializer(AbstractSerializer):
    class Meta:
        model = models.Catalog
        fields = ['id', 'nazev', 'obrazek_id', 'products_ids', 'attributes_ids']
