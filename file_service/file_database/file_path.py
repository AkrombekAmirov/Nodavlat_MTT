from os.path import join, dirname


async def get_file_database_path(name: str):
    return join(dirname(__file__), name)
