import subprocess
from datetime import datetime
from backup_file.file_path import get_file_path


def backup_postgres():
    # Fayl nomi (sanani qo'shish)
    backup_file = get_file_path(f"Database_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.sql")

    # Docker konteyner ichidagi pg_dump buyrug'ini ishlatish
    command = [
        'docker', 'exec', 'NTMO_kontrakt',
        'pg_dump', '-U', 'admin_user', 'NTMO_database'
    ]

    # Faylga yozish
    with open(f'{backup_file}', 'w') as f:
        try:
            # pg_dump buyrug'ini ishga tushirish
            subprocess.run(command, stdout=f, stderr=subprocess.PIPE, check=True)
            print(f"Backup muvaffaqiyatli olindi: {backup_file}")
        except subprocess.CalledProcessError as e:
            print(f"Backup olishda xatolik: {e.stderr.decode()}")


if __name__ == "__main__":
    backup_postgres()