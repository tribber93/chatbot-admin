# utils.py
import os
from dotenv import load_dotenv, set_key

def update_env_variable(key, value, env_path='.env'):
    """
    Memperbarui nilai variabel di file .env.
    
    :param key: Nama variabel lingkungan
    :param value: Nilai baru untuk variabel
    :param env_path: Path ke file .env
    """
    load_dotenv(env_path)  # Memuat variabel lingkungan saat ini
    set_key(env_path, key, value)  # Memperbarui nilai variabel
