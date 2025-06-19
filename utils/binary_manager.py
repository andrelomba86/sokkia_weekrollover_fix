import os
import platform
import sys

class BinaryManager:
    def __init__(self):
        self.root_path = self._get_root_path()
        self.system = platform.system().lower()
        
    def _get_root_path(self):
        """Retorna o caminho raiz do projeto"""
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    def get_binary_path(self, binary_name):
        """
        Retorna o caminho completo para o binário específico do sistema
        
        Args:
            binary_name (str): Nome do binário sem extensão
            
        Returns:
            str: Caminho completo para o binário
        """
        if self.system == 'windows':
            binary_name = f"{binary_name}.exe"
            bin_path = os.path.join(self.root_path, 'bin', 'windows', binary_name)
        else:
            bin_path = os.path.join(self.root_path, 'bin', 'linux', binary_name)
            
        if not os.path.exists(bin_path):
            raise FileNotFoundError(f"Binary not found: {bin_path}")
            
        return bin_path

    def get_binary_dir(self):
        """Retorna o diretório dos binários para o sistema atual"""
        return os.path.join(self.root_path, 'bin', self.system)
