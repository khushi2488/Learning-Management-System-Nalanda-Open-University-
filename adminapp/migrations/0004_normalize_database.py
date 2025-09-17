# Save this as: adminapp/migrations/0004_normalize_database.py

from django.db import migrations, models
import django.db.models.deletion


def migrate_data_forward(apps, schema_editor):
    """Safely migrate existing data to new structure"""
    try:
        # Get models
        StudentActivity = apps.get_model('adminapp', 'StudentActivity')
        Program = apps.get_model('adminapp', 'Program')
        Branch = apps.get_model('adminapp', 'Branch')
        Year = apps.get_model('adminapp', 'Year')
        ProgramStats = apps.get_model('adminapp', 'ProgramStats')
        BranchStats = apps.get_model('adminapp', 'BranchStats')
        
        # Migrate StudentActivity data
        for activity in StudentActivity.objects.all():
            try:
                if activity.program:
                    program_obj, _ = Program.objects.get_or_create(program=activity.program)
                    activity.program_fk_temp = program_obj
                
                if activity.branch:
                    branch_obj, _ = Branch.objects.get_or_create(branch=activity.branch)
                    activity.branch_fk_temp = branch_obj
                            
                if activity.year:
                    year_obj, _ = Year.objects.get_or_create(year=activity.year)
                    activity.year_fk_temp = year_obj
                
                activity.save()
            except Exception as e:
                print(f"Error migrating activity {activity.id}: {e}")
                continue
        
        # Migrate ProgramStats data
        for stats in ProgramStats.objects.all():
            try:
                if stats.program:
                    program_obj, _ = Program.objects.get_or_create(program=stats.program)
                    stats.program_fk_temp = program_obj
                    stats.save()
            except Exception as e:
                print(f"Error migrating program stats {stats.id}: {e}")
                continue
        
        # Migrate BranchStats data
        for stats in BranchStats.objects.all():
            try:
                if stats.branch:
                    branch_obj, _ = Branch.objects.get_or_create(branch=stats.branch)
                    stats.branch_fk_temp = branch_obj
                    stats.save()
            except Exception as e:
                print(f"Error migrating branch stats {stats.id}: {e}")
                continue
                
    except Exception as e:
        print(f"Migration error: {e}")


def migrate_data_reverse(apps, schema_editor):
    """Reverse migration"""
    pass


class Migration(migrations.Migration):
    
    dependencies = [
        ('adminapp', '0003_newscategory_alter_news_table_newsannouncement'),
    ]

    operations = [
        # Add temporary ForeignKey fields for StudentActivity
        migrations.AddField(
            model_name='studentactivity',
            name='program_fk_temp',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='adminapp.program'),
        ),
        migrations.AddField(
            model_name='studentactivity',
            name='branch_fk_temp',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='adminapp.branch'),
        ),
        migrations.AddField(
            model_name='studentactivity',
            name='year_fk_temp',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='adminapp.year'),
        ),
        
        # Add temporary ForeignKey fields for stats models
        migrations.AddField(
            model_name='programstats',
            name='program_fk_temp',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='adminapp.program'),
        ),
        migrations.AddField(
            model_name='branchstats',
            name='branch_fk_temp',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='adminapp.branch'),
        ),
        
        # Run data migration
        migrations.RunPython(migrate_data_forward, migrate_data_reverse),
    ]