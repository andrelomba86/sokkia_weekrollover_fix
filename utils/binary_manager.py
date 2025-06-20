import os
import platform


def get_gfzrnx_path():
    """
    Retorna o caminho completo para o binário gfzrnx específico do sistema

    Returns:
        str: Caminho completo para o binário gfzrnx
    """
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    system = platform.system().lower()

    if system == 'windows':
        bin_path = os.path.join(root_path, 'bin', 'windows', 'gfzrnx.exe')
    else:
        bin_path = os.path.join(root_path, 'bin', 'linux', 'gfzrnx')

    if not os.path.exists(bin_path):
        raise FileNotFoundError(f"Binary not found: {bin_path}")

    return bin_path
