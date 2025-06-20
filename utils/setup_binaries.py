import os
from utils.binary_manager import get_gfzrnx_path
from config.binaries import BINARY_CONFIG


def setup_binaries():
    """Configura as permissões do binário gfzrnx no Linux"""
    if os.name != 'nt':  # Se não for Windows
        try:
            gfzrnx_path = get_gfzrnx_path()
            if os.path.exists(gfzrnx_path):
                os.chmod(gfzrnx_path, BINARY_CONFIG['gfzrnx']['permissions'])
        except FileNotFoundError:
            pass
