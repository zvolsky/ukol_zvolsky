from rest_framework import serializers


class AttributeNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeName
        fields = ['id', 'nazev', 'kod', 'zobrazit']


class AttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        fields = ['id', 'hodnota']


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['id', 'nazev_atributu_id', 'hodnota_atributu_id']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'nazev', 'description', 'cena', 'mena', 'published_on', 'is_published']


class ProductAttributesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttributes
        fields = ['id', 'attribute', 'product']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'nazev', 'obrazek']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'obrazek_id', 'nazev']


class CatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Catalog
        fields = ['id', 'nazev', 'obrazek_id', 'products_ids', 'attributes_ids']
