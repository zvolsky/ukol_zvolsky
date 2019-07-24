# Generated by Django 2.2.3 on 2019-07-23 08:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='AttributeName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nazev', models.CharField(max_length=120, verbose_name='Name')),
                ('kod', models.CharField(blank=True, max_length=120, null=True, verbose_name='Code')),
                ('zobrazit', models.BooleanField(default=False, verbose_name='Show it')),
            ],
        ),
        migrations.CreateModel(
            name='AttributeValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hodnota', models.CharField(max_length=120, verbose_name='Value')),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nazev', models.CharField(blank=True, max_length=180, null=True, verbose_name='Name')),
                ('obrazek', models.URLField(verbose_name='Source URL')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nazev', models.CharField(max_length=180, verbose_name='Name')),
                ('description', models.TextField(verbose_name='Description')),
                ('cena', models.DecimalField(decimal_places=2, max_digits=9, verbose_name='Price')),
                ('mena', models.CharField(choices=[('CZK', 'CZK'), ('EUR', 'EUR')], default='CZK', max_length=3, verbose_name='Currency')),
                ('published_on', models.DateTimeField(blank=True, null=True, verbose_name='Published_on')),
                ('is_published', models.BooleanField(default=False, verbose_name='Is published?')),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nazev', models.CharField(max_length=180, verbose_name='Name')),
                ('obrazek_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_api.Image', verbose_name='Image')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_api.Product', verbose_name='Product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductAttributes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_api.Attribute', verbose_name='Attribute')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_api.Product', verbose_name='Product')),
            ],
        ),
        migrations.CreateModel(
            name='Catalog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nazev', models.CharField(max_length=180, verbose_name='Name')),
                ('attributes_ids', models.ManyToManyField(related_name='_catalog_attributes_ids_+', to='product_api.Attribute', verbose_name='Attributes')),
                ('obrazek_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_api.Image', verbose_name='Image')),
                ('products_ids', models.ManyToManyField(related_name='catalogs', to='product_api.Product', verbose_name='Products')),
            ],
        ),
        migrations.AddField(
            model_name='attribute',
            name='hodnota_atributu_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_api.AttributeValue', verbose_name='Attribute value'),
        ),
        migrations.AddField(
            model_name='attribute',
            name='nazev_atributu_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_api.AttributeName', verbose_name='Attribute name'),
        ),
    ]