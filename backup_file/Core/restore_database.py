import subprocess
from backup_file.file_path import get_file_path


def restore_postgres(backup_file):
    # Backup faylini tiklash uchun psql buyrug'ini chaqirish
    command = [
        'docker', 'exec', '-i', 'NTMO_kontrakt1',
        'psql', '-U', 'admin_user1', '-d', 'NTMO_database1'
    ]

    # Backup faylni o'qib, psql orqali tiklash
    with open(backup_file, 'r') as f:
        try:
            subprocess.run(command, stdin=f, check=True)
            print(f"Backup tiklandi: {backup_file}")
        except subprocess.CalledProcessError as e:
            print(f"Backup tiklashda xatolik: {e.stderr.decode()}")


if __name__ == "__main__":
    restore_postgres(get_file_path('Database__2024-10-21_12-00-16.sql'))