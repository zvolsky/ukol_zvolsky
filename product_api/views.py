import json

from django.db import transaction
from django.http import Http404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


from . import models, serializers


MODELSWITCH = {
    'attributename': (models.AttributeName, serializers.AttributeNameSerializer),
    'attributevalue': (models.AttributeValue, serializers.AttributeValueSerializer),
    'attribute': (models.Attribute, serializers.AttributeSerializer),
    'product': (models.Product, serializers.ProductSerializer),
    'productattributes': (models.ProductAttributes, serializers.ProductAttributesSerializer),
    'image': (models.Image, serializers.ImageSerializer),
    'productimage': (models.ProductImage, serializers.ProductImageSerializer),
    'catalog': (models.Catalog, serializers.CatalogSerializer),
}

# curl -i -X POST localhost:8000/import -H "Content-Type: application/json" --data-binary "@zadani/django-assignment/test_data.json"
class Import(APIView):
    """POST (or PUT) /import : import or update rows in the database from a list of mappings: {tablename: {"id":NNN, <other_values>}}"""
    def put(self, request):
        errors = []

        def bad_request(msg):
            return Response({'errors': [msg]}, status=status.HTTP_400_BAD_REQUEST)

        def add_error(msg):
            errors.append(msg)

        '''
        def is_simple_editable_field(field):
            return (
                    field.editable
                    and not field.primary_key
                    and not isinstance(field, (ForeignObjectRel, RelatedField))
            )

        def update_from_dict(instance, attrs):
            allowed_field_names = {
                f.name for f in instance._meta.get_fields()
                if is_simple_editable_field(f)
            }
            for attr, val in attrs.items():
                if attr in allowed_field_names:
                    setattr(instance, attr, val)
        '''

        data = request.data
        if type(data) not in (list, tuple):
            return bad_request("list (of insert's and/or update's) is required")

        updates = []   # list of prepared changes
        index = {}     # index of id's in prepared changes
        inserted = updated = 0

        for i, item in enumerate(data):
            kv = item.items()
            if len(kv) != 1:
                add_error("each item must contain 1 key (model name) and 1 value (inserted or updated values), which fails for: item %s" % i)
                continue

            for key, values in kv:
                break

            Model, Serializer = ModelSwitch.classes(key)
            if Model is None:
                add_error("each item must contain 1 key which must be a known model name, which fails for: item %s, %s" % (i, key))
                continue

            pk = values.get('id')
            if pk is None:
                add_error("each item must contain the value 'id', which fails for: item %s, %s" % (i, key))
                continue

            updates_key = (Model, pk)
            pos = index.get(updates_key)
            if pos is None:
                try:
                    row = Model.objects.get(pk=pk)
                except Model.DoesNotExist:
                    row = None
                if row is None:   # id not prepared for update and not in db
                    serializer = Serializer(data=values)
                    inserted += 1
                else:             # id not prepared for update but exists in db
                    new = row.__dict__.copy()
                    new.update(**values)
                    serializer = Serializer(data=new)
                    updated += 1
            else:                 # id already prepared from an earlier item in this import
                new = updates[pos].initial_data.copy()
                new.update(**values)
                serializer = Serializer(data=new)
            #if serializer.is_valid():
            if pos is None:
                index[updates_key] = len(updates)
                updates.append(serializer)
            else:
                updates[pos] = serializer
            #else:
            #    err = []
            #    for k in serializer.errors:
            #        err.append('%s : %s' % (k, ', '.join(serializer.errors[k])))
            #    add_error("data aren't valid for: item %s, %s, id %s (%s)" % (i, key, pk, '; '.join(err)))

        if not errors:
            failed = False
            serializer = None
            try:
                with transaction.atomic():     # This code executes inside a transaction
                    for serializer in updates:
                        if serializer.is_valid() and not failed:
                            try:
                                serializer.save()
                            except Exception as exc:
                                failed = True
                                msg = "cannot update database (integrity error or so)"
                                if serializer:
                                    add_error('%s, %s id %s' % (msg, serializer.__class__, serializer.validated_data['id']))
                                else:
                                    add_error(msg)
                        else:
                            failed = True
                            err = []
                            for k in serializer.errors:
                                err.append('%s : %s' % (k, ', '.join(serializer.errors[k])))
                            add_error("data aren't valid for: item %s, %s, id %s (%s)" % (i, key, pk, '; '.join(err)))
                    if failed:
                        pass  # raise RuntimeError  # break transaction
            except RuntimeError:
                pass   # we have errors collected already

        if errors:
            return Response({'errors': errors}, status=status.HTTP_201_CREATED)  # HTTP_400_BAD_REQUEST
        else:
            return Response({'inserted': updated, 'inserted': updated}, status=status.HTTP_201_CREATED)

    post = put


# curl -i -X GET localhost:8000/detail/product/ -H "Content-Type: application/json"
class List(APIView):
    """GET /detail/<tablename>/ : list all rows from the table <tablename>"""
    def get(self, request, model, format=None):
        Model, Serializer = ModelSwitch.classes(model)
        if Model is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        rows = Model.objects.all()
        serializer = Serializer(rows, many=True, as_list=True)
        return Response([row['id'] for row in serializer.data])  # returns id's as list; use this if all serializers return id only
        # return Response(serializer.data)                       # returns list of dict (fields); use this if serializers should return different fields


# curl -i -X GET localhost:8000/detail/product/1 -H "Content-Type: application/json"
class Detail(APIView):
    """GET /detail/<tablename>/<pk> : list all fields from the table <tablename> at the row with id <pk>"""
    def get(self, request, model, pk, format=None):
        Model, Serializer = ModelSwitch.classes(model)
        if Model is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            row = Model.objects.get(pk=pk)
        except Model.DoesNotExist:
            raise Http404
            # return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = Serializer(row)
        return Response(serializer.data)


class ModelSwitch:
    @staticmethod
    def classes(model):
        return MODELSWITCH.get(model.lower(), (None, None))
