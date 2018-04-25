# Generated by Django 2.0.4 on 2018-04-24 22:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=64)),
                ('token', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('network_id', models.CharField(max_length=64)),
                ('name', models.CharField(blank=True, max_length=64, null=True)),
                ('username', models.CharField(max_length=64)),
                ('age', models.IntegerField(blank=True, null=True)),
                ('distance', models.FloatField(blank=True, null=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='hornet.Account')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('network_id', models.CharField(max_length=64)),
                ('text', models.TextField()),
                ('datetime', models.DateTimeField()),
                ('type', models.CharField(choices=[('chat', 'chat'), ('private_request', 'private_request'), ('sticker', 'sticker'), ('share_photo', 'share_photo'), ('location', 'location')], max_length=64)),
                ('is_incoming', models.BooleanField()),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hornet.Member')),
            ],
        ),
    ]
