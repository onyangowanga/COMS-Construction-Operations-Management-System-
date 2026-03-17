from django.db import migrations, models


def backfill_variation_sequence(apps, schema_editor):
    VariationOrder = apps.get_model('variations', 'VariationOrder')

    variations = VariationOrder.objects.select_related('project').order_by('project_id', 'created_at', 'id')
    scoped_sequences = {}

    for variation in variations:
        scope_key = variation.project_id
        next_sequence = scoped_sequences.get(scope_key, 0) + 1
        scoped_sequences[scope_key] = next_sequence

        variation.sequence = next_sequence
        variation.save(update_fields=['sequence'])


class Migration(migrations.Migration):

    dependencies = [
        ('variations', '0002_variationorder_certified_amount_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variationorder',
            name='reference_number',
            field=models.CharField(help_text='Unique variation order reference (e.g., VO-2026-001)', max_length=50),
        ),
        migrations.AddField(
            model_name='variationorder',
            name='sequence',
            field=models.IntegerField(default=0, help_text='Sequence component used for variation reference generation'),
            preserve_default=False,
        ),
        migrations.RunPython(backfill_variation_sequence, migrations.RunPython.noop),
        migrations.AddIndex(
            model_name='variationorder',
            index=models.Index(fields=['project', 'sequence'], name='variationor_project_4d75e7_idx'),
        ),
        migrations.AddConstraint(
            model_name='variationorder',
            constraint=models.UniqueConstraint(fields=('project', 'sequence'), name='unique_variation_sequence_per_project'),
        ),
    ]