from django.db import migrations, models


RECONCILE_SUPABASE_SCHEMA = """
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'newspaper_edition' AND column_name = 'date'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'newspaper_edition' AND column_name = 'edition_date'
    ) THEN
        ALTER TABLE newspaper_edition RENAME COLUMN date TO edition_date;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'newspaper_edition' AND column_name = 'pdf'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'newspaper_edition' AND column_name = 'pdf_file'
    ) THEN
        ALTER TABLE newspaper_edition RENAME COLUMN pdf TO pdf_file;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'newspaper_edition' AND column_name = 'uploaded_at'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'newspaper_edition' AND column_name = 'created_at'
    ) THEN
        ALTER TABLE newspaper_edition RENAME COLUMN uploaded_at TO created_at;
    END IF;

    ALTER TABLE newspaper_edition
        ADD COLUMN IF NOT EXISTS title varchar(200) NOT NULL DEFAULT 'Untitled Edition',
        ADD COLUMN IF NOT EXISTS cover_image varchar(1000) NULL,
        ADD COLUMN IF NOT EXISTS description text NOT NULL DEFAULT '',
        ADD COLUMN IF NOT EXISTS is_published boolean NOT NULL DEFAULT true,
        ADD COLUMN IF NOT EXISTS updated_at timestamp with time zone NOT NULL DEFAULT now(),
        ADD COLUMN IF NOT EXISTS uploaded_by_id bigint NULL;

    ALTER TABLE newspaper_edition
        ALTER COLUMN pdf_file TYPE varchar(1000),
        ALTER COLUMN cover_image TYPE varchar(1000);

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'newspaper_edition' AND column_name = 'edition_date'
    ) THEN
        ALTER TABLE newspaper_edition ALTER COLUMN edition_date SET NOT NULL;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'newspaper_edition' AND column_name = 'pdf_file'
    ) THEN
        ALTER TABLE newspaper_edition ALTER COLUMN pdf_file SET NOT NULL;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'newspaper_edition_uploaded_by_id_fkey'
    ) THEN
        ALTER TABLE newspaper_edition
            ADD CONSTRAINT newspaper_edition_uploaded_by_id_fkey
            FOREIGN KEY (uploaded_by_id)
            REFERENCES auth_user(id)
            DEFERRABLE INITIALLY DEFERRED;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS newspaper_e_edition_958ca5_idx
    ON newspaper_edition (edition_date);

CREATE INDEX IF NOT EXISTS newspaper_e_is_publ_0d10e4_idx
    ON newspaper_edition (is_published);

CREATE INDEX IF NOT EXISTS newspaper_edition_uploaded_by_id_idx
    ON newspaper_edition (uploaded_by_id);
"""


class Migration(migrations.Migration):

    dependencies = [
        ('newspaper', '0002_add_view_count'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=RECONCILE_SUPABASE_SCHEMA,
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name='edition',
                    name='pdf_file',
                    field=models.URLField(max_length=1000),
                ),
                migrations.AlterField(
                    model_name='edition',
                    name='cover_image',
                    field=models.URLField(blank=True, max_length=1000, null=True),
                ),
                migrations.AddIndex(
                    model_name='edition',
                    index=models.Index(
                        fields=['edition_date'],
                        name='newspaper_e_edition_958ca5_idx',
                    ),
                ),
                migrations.AddIndex(
                    model_name='edition',
                    index=models.Index(
                        fields=['is_published'],
                        name='newspaper_e_is_publ_0d10e4_idx',
                    ),
                ),
            ],
        ),
    ]
