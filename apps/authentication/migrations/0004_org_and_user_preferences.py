from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_projectaccess_project_projectaccess_user_user_groups_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='default_currency',
            field=models.CharField(default='KES', help_text='Default organization currency (ISO 4217)', max_length=3),
        ),
        migrations.AddField(
            model_name='organization',
            name='fiscal_year_start',
            field=models.CharField(default='January 1', help_text='Fiscal year start label', max_length=20),
        ),
        migrations.AddField(
            model_name='user',
            name='ui_compact_mode',
            field=models.BooleanField(default=False, help_text='Use compact UI layout'),
        ),
        migrations.AddField(
            model_name='user',
            name='ui_language',
            field=models.CharField(default='en', help_text='Preferred UI language', max_length=8),
        ),
        migrations.AddField(
            model_name='user',
            name='ui_theme',
            field=models.CharField(choices=[('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto')], default='light', help_text='Preferred UI theme', max_length=10),
        ),
        migrations.AddField(
            model_name='user',
            name='ui_timezone',
            field=models.CharField(default='Africa/Nairobi', help_text='Preferred UI timezone', max_length=64),
        ),
    ]
