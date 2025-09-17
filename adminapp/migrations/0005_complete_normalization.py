# Create this as: adminapp/migrations/0005_complete_normalization.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0004_normalize_database'),
    ]

    operations = [
        # Step 1: Remove old CharField fields
        migrations.RemoveField(
            model_name='studentactivity',
            name='program',
        ),
        migrations.RemoveField(
            model_name='studentactivity',
            name='branch',
        ),
        migrations.RemoveField(
            model_name='studentactivity',
            name='year',
        ),
        migrations.RemoveField(
            model_name='programstats',
            name='program',
        ),
        migrations.RemoveField(
            model_name='branchstats',
            name='branch',
        ),

        # Step 2: Rename temporary fields to final names
        migrations.RenameField(
            model_name='studentactivity',
            old_name='program_fk_temp',
            new_name='program',
        ),
        migrations.RenameField(
            model_name='studentactivity',
            old_name='branch_fk_temp',
            new_name='branch',
        ),
        migrations.RenameField(
            model_name='studentactivity',
            old_name='year_fk_temp',
            new_name='year',
        ),
        migrations.RenameField(
            model_name='programstats',
            old_name='program_fk_temp',
            new_name='program',
        ),
        migrations.RenameField(
            model_name='branchstats',
            old_name='branch_fk_temp',
            new_name='branch',
        ),

        # Step 3: Make ForeignKeys non-nullable (optional - remove if you want them nullable)
        migrations.AlterField(
            model_name='studentactivity',
            name='program',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminapp.program'),
        ),
        migrations.AlterField(
            model_name='studentactivity',
            name='branch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminapp.branch'),
        ),
        migrations.AlterField(
            model_name='studentactivity',
            name='year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminapp.year'),
        ),
        migrations.AlterField(
            model_name='programstats',
            name='program',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminapp.program'),
        ),
        migrations.AlterField(
            model_name='branchstats',
            name='branch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminapp.branch'),
        ),
    ]