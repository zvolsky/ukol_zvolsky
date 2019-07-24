from datetime import datetime
from operator import itemgetter

from logzero import logger

from django.db import transaction
from django.http import Http404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


from . import models, serializers

FAILURE_STOP = False   # with first error stop update the database but preserve previous changes
FAILURE_REVERT = True  # with first error revert all changes

FAILURE_MODE = FAILURE_REVERT  # FAILURE_STOP or FAILURE_REVERT


MODELSWITCH = {
    'attributename': (models.AttributeName, serializers.AttributeNameSerializer, 0),
    'attributevalue': (models.AttributeValue, serializers.AttributeValueSerializer, 1),
    'attribute': (models.Attribute, serializers.AttributeSerializer, 2),
    'product': (models.Product, serializers.ProductSerializer, 3),
    'productattributes': (models.ProductAttributes, serializers.ProductAttributesSerializer, 4),
    'image': (models.Image, serializers.ImageSerializer, 5),
    'productimage': (models.ProductImage, serializers.ProductImageSerializer, 6),
    'catalog': (models.Catalog, serializers.CatalogSerializer, 7),  # last one is import order (imports need sorting before they can be applied, with regard to FK)
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

        def model():  # for error reporting only
            return str(serializer.__class__)[32:-12]  # <class 'product_api.serializers.ProductSerializer'>  ->   Product

        def log_import():
            msg = 'import - inserted %s, updated %s'
            if errors:
                logger.error(msg % (inserted, updated) + ' - errors (!)')
                for err in errors:
                    logger.warning(err)
            else:
                logger.info(msg % (inserted, updated))

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

            Model, Serializer, import_order = ModelSwitch.classes(key)
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
                    serializer = Serializer(row, data=values)   # we will use this for validation, but ...
                    # ... no idea how to force Update instead of Insert, so lets update using the model-instance
                    #   which (as everything) is not easy in Django, but see models.py:UpdateMixin
                index[updates_key] = len(updates)
                updates.append([serializer, import_order, row])  # row we need for the Update (using Model instead of Serializer) mentioned above
            else:                 # id already prepared from an earlier item in this import
                values.update(updates[pos][0].initial_data)
                updates[pos][0] = Serializer(data=values)

        updates.sort(key=itemgetter(1))  # if we sort models into order based on FK dependencies, we can save the import in some cases (stable sort is good here!)
        index = None   # not used anymore, but to be sure; because after the Sort is Index invalidated

        if not errors:
            failed = False
            try:
                with transaction.atomic():     # This code executes inside a transaction
                    for serializer, _import_order, row in updates:
                        if serializer.is_valid():
                            if not failed:     # we will never update the db more after the 1st error
                                required_id = serializer.initial_data.get('id')
                                try:
                                    if row:   # Update instead of Insert (because I have no idea how to implement such a stupid thing with serializer itself)
                                        if row.update(**serializer.validated_data):   # see models.py:UpdateMixin
                                            updated += 1
                                        instance = row
                                    else:
                                        instance = serializer.save()
                                except Exception as exc:
                                    # raise exc  # for Debug purposes
                                    failed = True
                                    add_error("cannot update database (integrity error,..), %s %s" % (model(), serializer.initial_data))
                                if not failed and required_id and instance.id != required_id:   # not saved as expected ('if not failed' is necessary, otherwise 'instance' is missing)
                                    failed = True
                                    if FAILURE_MODE == FAILURE_STOP:  # we want preserve all previous, but this instance is corrupted
                                        instance.delete()
                                    add_error("id order mismatch, different id expected, %s %s but id %s received" % (model(), serializer.initial_data, instance.id))
                        else:
                            failed = True
                            err = []
                            for k in serializer.errors:
                                err.append('%s : %s' % (k, ', '.join(serializer.errors[k])))
                            add_error("data aren't valid: %s %s (%s)" % (model(), serializer.initial_data, '; '.join(err)))
                    if FAILURE_MODE == FAILURE_REVERT and failed:
                        raise RuntimeError  # break+revert transaction
            except RuntimeError as exc:     # this is just to continue after transaction is reverted
                inserted = updated = 0
            except transaction.TransactionManagementError as exc:
                inserted = updated = 0
                add_error("+ transaction.TransactionManagementError (more SQL commands after Rollback)")

        results = {'inserted': inserted, 'updated': updated}
        if errors:
            results.update({'errors': errors})
        log_import()
        return Response(results, status=status.HTTP_400_BAD_REQUEST if errors and FAILURE_MODE == FAILURE_REVERT else status.HTTP_201_CREATED)

    post = put    # POST: because required in task assignment ; PUT: because of idempotent behaviour


# curl -i -X GET localhost:8000/detail/product/ -H "Content-Type: application/json"
class List(APIView):
    """GET /detail/<tablename>/ : list all rows from the table <tablename>"""
    def get(self, request, model, format=None):
        Model, Serializer, _import_order = ModelSwitch.classes(model)
        if Model is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        rows = Model.objects.all()
        serializer = Serializer(rows, many=True, as_list=True)
        return Response([row['id'] for row in serializer.data])  # returns id's as list; use this if all serializers return id only
        # return Response(serializer.data)                       # returns list of dict (fields); use this if serializers should return different fields (have different list_fields)


# curl -i -X GET localhost:8000/detail/product/1 -H "Content-Type: application/json"
class Detail(APIView):
    """GET /detail/<tablename>/<pk> : list all fields from the table <tablename> at the row with id <pk>"""
    def get(self, request, model, pk, format=None):
        Model, Serializer, _import_order = ModelSwitch.classes(model)
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
