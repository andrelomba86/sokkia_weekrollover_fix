import os
import sys
from bin.config import BINARY_CONFIG
import platform


def get_gfzrnx_path():
    """
    Returns the full path to the system-specific gfzrnx binary,
    compatible with both development and PyInstaller environments.

    Returns:
        str: Full path to the gfzrnx binary
    """
    system = platform.system().lower()

    # Detecta se está rodando via PyInstaller
    is_compiled = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
    if is_compiled:
        # PyInstaller: binários estão em sys._MEIPASS
        root_path = os.path.dirname(sys.executable)
    else:
        # Ambiente normal (dev)
        root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if is_compiled:
        if system == 'windows':
            bin_path = os.path.join(root_path, 'gfzrnx.exe')
        else:
            bin_path = os.path.join(root_path, 'gfzrnx')
    else:
        if system == 'windows':
            bin_path = os.path.join(root_path, 'bin', 'windows', 'gfzrnx.exe')
        else:
            bin_path = os.path.join(root_path, 'bin', 'linux', 'gfzrnx')

    if not os.path.exists(bin_path):
        raise FileNotFoundError(f"Binary not found: {bin_path}")

    return bin_path


def setup_permissions():
    """Sets the permissions for the gfzrnx binary on Linux"""
    if os.name != 'nt':  # If not Windows
        try:
            gfzrnx_path = get_gfzrnx_path()
            if os.path.exists(gfzrnx_path):
                os.chmod(gfzrnx_path, BINARY_CONFIG['gfzrnx']['permissions'])
        except FileNotFoundError:
            pass
