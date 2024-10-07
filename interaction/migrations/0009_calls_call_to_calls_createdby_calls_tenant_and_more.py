# Generated by Django 4.1 on 2024-10-05 09:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0001_initial'),
        ('contacts', '0002_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('interaction', '0008_calls_call_to_calls_createdby_calls_tenant_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='calls',
            name='call_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='call_to_meetings', to='contacts.contact', verbose_name='Contact Name'),
        ),
        migrations.AddField(
            model_name='calls',
            name='createdBy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_calls', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='calls',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tenant.tenant'),
        ),
        migrations.AddField(
            model_name='conversation',
            name='date_time',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='conversation',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tenant.tenant'),
        ),
        migrations.AddField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(related_name='groups', to='contacts.contact'),
        ),
        migrations.AddField(
            model_name='group',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tenant.tenant'),
        ),
        migrations.AddField(
            model_name='interaction',
            name='entity_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='interaction',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tenant.tenant'),
        ),
        migrations.AddField(
            model_name='meetings',
            name='assigned_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='meeting_assigned_users', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='meetings',
            name='contact_name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='meeting_contacts', to='contacts.contact', verbose_name='Contact Name'),
        ),
        migrations.AddField(
            model_name='meetings',
            name='createdBy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='meeting_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='meetings',
            name='host',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='meeting_hosts', to=settings.AUTH_USER_MODEL, verbose_name='Host'),
        ),
        migrations.AddField(
            model_name='meetings',
            name='participants',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='meeting_participants', to='contacts.contact'),
        ),
        migrations.AddField(
            model_name='meetings',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tenant.tenant'),
        ),
    ]
