from django.db import migrations, models


def backfill_lpo_sequence(apps, schema_editor):
    LocalPurchaseOrder = apps.get_model('suppliers', 'LocalPurchaseOrder')

    lpos = LocalPurchaseOrder.objects.select_related('project').order_by('project_id', 'issue_date', 'created_at', 'id')
    scoped_sequences = {}

    for lpo in lpos:
        scope_key = lpo.project_id
        next_sequence = scoped_sequences.get(scope_key, 0) + 1
        scoped_sequences[scope_key] = next_sequence

        lpo.sequence = next_sequence
        lpo.save(update_fields=['sequence'])


class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0002_alter_localpurchaseorder_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='localpurchaseorder',
            name='lpo_number',
            field=models.CharField(help_text='Unique LPO number', max_length=50),
        ),
        migrations.AddField(
            model_name='localpurchaseorder',
            name='sequence',
            field=models.IntegerField(default=0, help_text='Sequence component used for LPO number generation'),
            preserve_default=False,
        ),
        migrations.RunPython(backfill_lpo_sequence, migrations.RunPython.noop),
        migrations.AddIndex(
            model_name='localpurchaseorder',
            index=models.Index(fields=['project', 'sequence'], name='local_purch_project_f33786_idx'),
        ),
        migrations.AddConstraint(
            model_name='localpurchaseorder',
            constraint=models.UniqueConstraint(fields=('project', 'sequence'), name='unique_lpo_sequence_per_project'),
        ),
    ]