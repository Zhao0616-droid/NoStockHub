from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_align_init_sql_user_schema'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.URLField(blank=True, max_length=500, verbose_name='头像URL'),
        ),
    ]
