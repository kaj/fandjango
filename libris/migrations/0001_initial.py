# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-29 00:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('subtitle', models.CharField(max_length=500)),
                ('note', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='CreativePart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.CharField(blank=True, max_length=200)),
                ('role', models.CharField(blank=True, max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Creator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('slug', models.SlugField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='DaystripRun',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fromdate', models.DateField()),
                ('todate', models.DateField()),
                ('is_sundays', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Episode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('episode', models.CharField(max_length=200)),
                ('teaser', models.TextField(blank=True)),
                ('note', models.TextField(blank=True)),
                ('firstpub', models.DateField(blank=True, null=True)),
                ('copyright', models.CharField(blank=True, max_length=200)),
                ('daystrip', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='libris.DaystripRun')),
            ],
        ),
        migrations.CreateModel(
            name='ForeignName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('language', models.CharField(max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveSmallIntegerField()),
                ('number', models.PositiveSmallIntegerField()),
                ('numberStr', models.CharField(help_text=b'number in char form, or e.g. "19-20" for double.', max_length=5)),
                ('pages', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('cover_best', models.PositiveSmallIntegerField(blank=True, default=0, help_text=b'Position of this cover in yearly competition.')),
                ('ordering', models.PositiveIntegerField()),
                ('cover_by', models.ManyToManyField(blank=True, null=True, to='libris.Creator')),
            ],
            options={
                'ordering': ('ordering',),
            },
        ),
        migrations.CreateModel(
            name='OtherMag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('issue', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('i_of', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('year', models.PositiveSmallIntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordno', models.PositiveSmallIntegerField(default=4711)),
                ('label', models.CharField(blank=True, max_length=200)),
                ('best_plac', models.PositiveSmallIntegerField(blank=True, default=0, help_text=b'Position of this episode in yearly competition.')),
                ('part_no', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('part_name', models.CharField(blank=True, max_length=200)),
                ('article', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='libris.Article')),
                ('episode', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='libris.Episode')),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='libris.Issue')),
            ],
            options={
                'ordering': ('issue__ordering', 'ordno'),
            },
        ),
        migrations.CreateModel(
            name='RefKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('kind', models.CharField(choices=[(b'F', b'Fantomen'), (b'T', b'Serietitel'), (b'P', b'Real-life person (artist, writer, etc)'), (b'X', b'In-story object')], default=b'X', max_length=1)),
                ('slug', models.SlugField()),
            ],
            options={
                'ordering': ('kind', 'title'),
            },
        ),
        migrations.CreateModel(
            name='Title',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, unique=True)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'ordering': ('title',),
            },
        ),
        migrations.AlterUniqueTogether(
            name='refkey',
            unique_together=set([('kind', 'title'), ('kind', 'slug')]),
        ),
        migrations.AddField(
            model_name='episode',
            name='orig_name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='libris.ForeignName'),
        ),
        migrations.AddField(
            model_name='episode',
            name='prevpub',
            field=models.ManyToManyField(blank=True, to='libris.OtherMag'),
        ),
        migrations.AddField(
            model_name='episode',
            name='ref_keys',
            field=models.ManyToManyField(blank=True, to='libris.RefKey'),
        ),
        migrations.AddField(
            model_name='episode',
            name='title',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='libris.Title'),
        ),
        migrations.AddField(
            model_name='creativepart',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='libris.Creator'),
        ),
        migrations.AddField(
            model_name='creativepart',
            name='episode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='libris.Episode'),
        ),
        migrations.AddField(
            model_name='article',
            name='creators',
            field=models.ManyToManyField(to='libris.Creator'),
        ),
        migrations.AddField(
            model_name='article',
            name='ref_keys',
            field=models.ManyToManyField(to='libris.RefKey'),
        ),
        migrations.AlterUniqueTogether(
            name='publication',
            unique_together=set([('issue', 'episode', 'article')]),
        ),
        migrations.AlterUniqueTogether(
            name='issue',
            unique_together=set([('year', 'number')]),
        ),
        migrations.AlterUniqueTogether(
            name='creativepart',
            unique_together=set([('episode', 'creator', 'role')]),
        ),
    ]
