import re

from django.db import migrations, models
import django.db.models.deletion


def backfill_subcontract_identifiers(apps, schema_editor):
    Project = apps.get_model('projects', 'Project')
    Organization = apps.get_model('authentication', 'Organization')
    SubcontractAgreement = apps.get_model('subcontracts', 'SubcontractAgreement')
    SubcontractClaim = apps.get_model('subcontracts', 'SubcontractClaim')

    contract_sequences = {}
    contracts = SubcontractAgreement.objects.select_related('project', 'project__organization').order_by('created_at', 'id')

    for contract in contracts:
        organization_id = contract.project.organization_id if contract.project_id else None
        year_match = re.search(r'(\d{4})', contract.contract_reference or '')
        year = int(year_match.group(1)) if year_match else contract.created_at.year
        scope_key = (organization_id, year)
        next_sequence = contract_sequences.get(scope_key, 0) + 1
        contract_sequences[scope_key] = next_sequence

        contract.organization_id = organization_id
        contract.year = year
        contract.sequence = next_sequence
        contract.save(update_fields=['organization', 'year', 'sequence'])

    claim_sequences = {}
    claims = SubcontractClaim.objects.select_related('subcontract', 'subcontract__project').order_by('created_at', 'id')

    for claim in claims:
        project_id = claim.subcontract.project_id if claim.subcontract_id else None
        next_sequence = claim_sequences.get(project_id, 0) + 1
        claim_sequences[project_id] = next_sequence

        claim.project_id = project_id
        claim.sequence = next_sequence
        claim.save(update_fields=['project', 'sequence'])


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_projectaccess_project_projectaccess_user_user_groups_and_more'),
        ('projects', '0002_project_year_sequence'),
        ('subcontracts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcontractagreement',
            name='organization',
            field=models.ForeignKey(blank=True, help_text='Organization owning this contract', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subcontract_agreements', to='authentication.organization'),
        ),
        migrations.AddField(
            model_name='subcontractagreement',
            name='year',
            field=models.IntegerField(default=0, help_text='Year component used for contract code generation'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subcontractagreement',
            name='sequence',
            field=models.IntegerField(default=0, help_text='Sequence component used for contract code generation'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='subcontractagreement',
            name='contract_reference',
            field=models.CharField(help_text='Unique contract reference number (e.g., SC-2026-001)', max_length=100),
        ),
        migrations.AddField(
            model_name='subcontractclaim',
            name='project',
            field=models.ForeignKey(blank=True, help_text='Project this claim belongs to', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subcontract_claims', to='projects.project'),
        ),
        migrations.AddField(
            model_name='subcontractclaim',
            name='sequence',
            field=models.IntegerField(default=0, help_text='Sequence component used for claim number generation'),
            preserve_default=False,
        ),
        migrations.RunPython(backfill_subcontract_identifiers, migrations.RunPython.noop),
        migrations.AddIndex(
            model_name='subcontractagreement',
            index=models.Index(fields=['organization', 'year', 'sequence'], name='subcontrac_organiz_41a7e1_idx'),
        ),
        migrations.AddConstraint(
            model_name='subcontractagreement',
            constraint=models.UniqueConstraint(fields=('organization', 'year', 'sequence'), name='unique_contract_sequence_per_org_year'),
        ),
        migrations.AddIndex(
            model_name='subcontractclaim',
            index=models.Index(fields=['project', 'sequence'], name='subcontrac_project_7b4f99_idx'),
        ),
        migrations.AddConstraint(
            model_name='subcontractclaim',
            constraint=models.UniqueConstraint(fields=('project', 'sequence'), name='unique_claim_sequence_per_project'),
        ),
    ]