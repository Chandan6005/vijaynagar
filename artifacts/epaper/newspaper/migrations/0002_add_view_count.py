from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newspaper', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='edition',
            name='view_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
