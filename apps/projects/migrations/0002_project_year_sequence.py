import re

from django.db import migrations, models


def backfill_project_year_sequence(apps, schema_editor):
    Project = apps.get_model('projects', 'Project')

    projects = Project.objects.select_related('organization').order_by('created_at', 'id')
    scoped_sequences = {}

    for project in projects:
        code = project.code or ''
        year_match = re.search(r'PRJ-(\d{4})-', code)
        year = int(year_match.group(1)) if year_match else project.created_at.year

        scope_key = (project.organization_id, year)
        next_sequence = scoped_sequences.get(scope_key, 0) + 1
        scoped_sequences[scope_key] = next_sequence

        project.year = year
        project.sequence = next_sequence
        project.save(update_fields=['year', 'sequence'])


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='year',
            field=models.IntegerField(default=0, help_text='Year component used for code generation'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='sequence',
            field=models.IntegerField(default=0, help_text='Sequence component used for code generation'),
            preserve_default=False,
        ),
        migrations.RunPython(backfill_project_year_sequence, migrations.RunPython.noop),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['organization', 'year', 'sequence'], name='projects_organiz_0d3d43_idx'),
        ),
        migrations.AddConstraint(
            model_name='project',
            constraint=models.UniqueConstraint(fields=('organization', 'year', 'sequence'), name='unique_project_sequence_per_org_year'),
        ),
    ]