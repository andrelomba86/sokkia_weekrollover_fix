import os
import stat
from utils.binary_manager import BinaryManager
from config.binaries import BINARY_CONFIG

def setup_binaries():
    """Configura os binários para o sistema atual"""
    binary_manager = BinaryManager()
    bin_dir = binary_manager.get_binary_dir()
    
    # Garante que o diretório existe
    os.makedirs(bin_dir, exist_ok=True)
    
    # Configura as permissões dos binários no Linux
    if binary_manager.system != 'windows':
        for binary_name in BINARY_CONFIG:
            binary_path = binary_manager.get_binary_path(binary_name)
            if os.path.exists(binary_path):
                os.chmod(binary_path, BINARY_CONFIG[binary_name]['permissions'])

def verify_binaries():
    """Verifica se todos os binários necessários estão presentes"""
    binary_manager = BinaryManager()
    missing = []
    
    for binary_name, config in BINARY_CONFIG.items():
        if config['required']:
            try:
                binary_manager.get_binary_path(binary_name)
            except FileNotFoundError:
                missing.append(binary_name)
    
    return missing

