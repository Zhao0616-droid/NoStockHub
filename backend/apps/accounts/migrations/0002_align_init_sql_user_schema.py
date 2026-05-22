# 当 DB 由 sql/init.sql 初始化且 accounts.0001 被 fake 时，缺少 AbstractUser 字段与 M2M 表。
# 也在「仅缺中间表」的情况下补建 accounts_user_groups / accounts_user_user_permissions。
from django.db import migrations


def _has_table(cursor, name):
    cursor.execute(
        """
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_schema = DATABASE() AND table_name = %s
        """,
        [name],
    )
    return cursor.fetchone()[0] > 0


def _has_column(cursor, table, column):
    cursor.execute(
        """
        SELECT COUNT(*) FROM information_schema.columns
        WHERE table_schema = DATABASE() AND table_name = %s AND column_name = %s
        """,
        [table, column],
    )
    return cursor.fetchone()[0] > 0


def align_accounts_schema(apps, schema_editor):
    if schema_editor.connection.vendor != 'mysql':
        return

    connection = schema_editor.connection
    with connection.cursor() as cursor:
        user_is_django_shape = _has_column(cursor, 'accounts_user', 'is_superuser')
        has_legacy_role_enum = _has_column(cursor, 'accounts_user', 'role')
        groups_ok = _has_table(cursor, 'accounts_user_groups')
        perms_ok = _has_table(cursor, 'accounts_user_user_permissions')

        if not user_is_django_shape:
            cursor.execute(
                """
                ALTER TABLE accounts_user
                  ADD COLUMN is_superuser TINYINT(1) NOT NULL DEFAULT 0,
                  ADD COLUMN first_name VARCHAR(150) NOT NULL DEFAULT '',
                  ADD COLUMN last_name VARCHAR(150) NOT NULL DEFAULT '',
                  ADD COLUMN is_staff TINYINT(1) NOT NULL DEFAULT 0,
                  ADD COLUMN date_joined DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                  ADD COLUMN role_type VARCHAR(20) NOT NULL DEFAULT 'member'
                """
            )
            if has_legacy_role_enum:
                cursor.execute('UPDATE accounts_user SET role_type = role')
                cursor.execute('ALTER TABLE accounts_user DROP COLUMN role')
            cursor.execute(
                """
                ALTER TABLE accounts_user
                  MODIFY COLUMN username VARCHAR(150) NOT NULL,
                  MODIFY COLUMN email VARCHAR(254) NOT NULL,
                  MODIFY COLUMN password VARCHAR(128) NOT NULL,
                  MODIFY COLUMN avatar VARCHAR(200) NOT NULL DEFAULT '',
                  MODIFY COLUMN phone VARCHAR(20) NOT NULL DEFAULT '',
                  MODIFY COLUMN last_login DATETIME(6) NULL
                """
            )

        if not groups_ok:
            cursor.execute(
                """
                CREATE TABLE accounts_user_groups (
                  id BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
                  user_id CHAR(36) NOT NULL,
                  group_id INT NOT NULL,
                  UNIQUE KEY accounts_user_groups_user_id_group_id_uniq (user_id, group_id),
                  CONSTRAINT accounts_user_groups_user_id_fk
                    FOREIGN KEY (user_id) REFERENCES accounts_user (id),
                  CONSTRAINT accounts_user_groups_group_id_fk
                    FOREIGN KEY (group_id) REFERENCES auth_group (id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
                """
            )

        if not perms_ok:
            cursor.execute(
                """
                CREATE TABLE accounts_user_user_permissions (
                  id BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
                  user_id CHAR(36) NOT NULL,
                  permission_id INT NOT NULL,
                  UNIQUE KEY accounts_user_user_permissions_user_id_perm_id_uniq (user_id, permission_id),
                  CONSTRAINT accounts_user_user_permissions_user_id_fk
                    FOREIGN KEY (user_id) REFERENCES accounts_user (id),
                  CONSTRAINT accounts_user_user_permissions_perm_id_fk
                    FOREIGN KEY (permission_id) REFERENCES auth_permission (id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
                """
            )


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(align_accounts_schema, migrations.RunPython.noop),
    ]
