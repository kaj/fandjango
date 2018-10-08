# Generated by Django 2.1.2 on 2018-10-08 09:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('libris', '0002_remove_redundant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='daystrip',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='libris.DaystripRun'),
        ),
        migrations.AlterField(
            model_name='episode',
            name='orig_name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='libris.ForeignName'),
        ),
        migrations.AlterField(
            model_name='episode',
            name='title',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='libris.Title'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='cover_best',
            field=models.PositiveSmallIntegerField(blank=True, default=0, help_text='Position of this cover in yearly competition.'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='numberStr',
            field=models.CharField(help_text='number in char form, or e.g. "19-20" for double.', max_length=5),
        ),
        migrations.AlterField(
            model_name='publication',
            name='best_plac',
            field=models.PositiveSmallIntegerField(blank=True, default=0, help_text='Position of this episode in yearly competition.'),
        ),
        migrations.AlterField(
            model_name='publication',
            name='issue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='libris.Issue'),
        ),
        migrations.AlterField(
            model_name='refkey',
            name='kind',
            field=models.CharField(choices=[('F', 'Fantomen'), ('T', 'Serietitel'), ('P', 'Real-life person (artist, writer, etc)'), ('X', 'In-story object')], default='X', max_length=1),
        ),
    ]
