import re

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models


def backfill_report_sequence(apps, schema_editor):
    Report = apps.get_model('reporting', 'Report')

    reports = Report.objects.select_related('organization').order_by('created_at', 'id')
    scoped_sequences = {}

    for report in reports:
        created_year = report.created_at.year if report.created_at else 0
        code = (report.code or '').strip()

        match = re.search(r'RPT-(\d{4})-(\d+)', code)
        year = int(match.group(1)) if match else created_year

        scope_key = (report.organization_id, year)
        next_sequence = scoped_sequences.get(scope_key, 0) + 1
        scoped_sequences[scope_key] = next_sequence

        report.year = year
        report.sequence = next_sequence
        report.code = f'RPT-{year}-{next_sequence:03d}'
        report.save(update_fields=['year', 'sequence', 'code'])


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='aggregations',
            field=models.JSONField(blank=True, default=dict, help_text='Aggregation configuration'),
        ),
        migrations.AddField(
            model_name='report',
            name='code',
            field=models.CharField(default='', help_text='Auto-generated report code (e.g., RPT-2026-001)', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='report',
            name='columns',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, default=list, help_text='Selected report columns', size=None),
        ),
        migrations.AddField(
            model_name='report',
            name='filters',
            field=models.JSONField(blank=True, default=dict, help_text='Report filters definition'),
        ),
        migrations.AddField(
            model_name='report',
            name='group_by',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, default=list, help_text='Grouping columns', size=None),
        ),
        migrations.AddField(
            model_name='report',
            name='module',
            field=models.CharField(default='general', help_text='Business module this report belongs to', max_length=100),
        ),
        migrations.AddField(
            model_name='report',
            name='sequence',
            field=models.IntegerField(default=0, help_text='Sequence number within organization year', validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='report',
            name='year',
            field=models.IntegerField(default=0, help_text='Year for sequence tracking'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='report',
            name='report_type',
            field=models.CharField(choices=[('TABLE', 'Table'), ('SUMMARY', 'Summary'), ('CHART', 'Chart'), ('PROJECT_FINANCIAL', 'Project Financial Summary'), ('CASH_FLOW', 'Cash Flow Forecast Report'), ('VARIATION_IMPACT', 'Variation Impact Report'), ('SUBCONTRACTOR_PAYMENT', 'Subcontractor Payment Report'), ('DOCUMENT_AUDIT', 'Document Audit Report'), ('PROCUREMENT_SUMMARY', 'Procurement Summary'), ('CUSTOM', 'Custom Report')], help_text='Type of report', max_length=50),
        ),
        migrations.RunPython(backfill_report_sequence, migrations.RunPython.noop),
        migrations.AddIndex(
            model_name='report',
            index=models.Index(fields=['module'], name='reporting_r_module_9c5d49_idx'),
        ),
        migrations.AddConstraint(
            model_name='report',
            constraint=models.UniqueConstraint(fields=('organization', 'year', 'sequence'), name='unique_report_sequence_per_org_year'),
        ),
    ]
