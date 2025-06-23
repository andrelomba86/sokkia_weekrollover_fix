import os
# from utils.binary_manager import get_gfzrnx_path
from bin.config import BINARY_CONFIG
import platform

def get_gfzrnx_path():
    """
    Returns the full path to the system-specific gfzrnx binary

    Returns:
        str: Full path to the gfzrnx binary
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


def setup_permissions():
    """Sets the permissions for the gfzrnx binary on Linux"""
    if os.name != 'nt':  # If not Windows
        try:
            gfzrnx_path = get_gfzrnx_path()
            if os.path.exists(gfzrnx_path):
                os.chmod(gfzrnx_path, BINARY_CONFIG['gfzrnx']['permissions'])
        except FileNotFoundError:
            pass
