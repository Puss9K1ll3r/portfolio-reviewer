import os
import zipfile
import re
from typing import List, Tuple

def validate_structure(zip_path: str, group: str, name: str, subject: str, expected_count: int) -> Tuple[bool, List[str]]:
    """Основная функция проверки структуры"""
    errors = []
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Проверка структуры папок
            required = [f"{group}/", f"{group}/{name}/", f"{group}/{name}/{subject}/"]
            for folder in required:
                if not any(n.startswith(folder) for n in zip_ref.namelist()):
                    errors.append(f"Missing folder: {folder}")
            
            # Проверка файлов
            files = [f for f in zip_ref.namelist() 
                   if f.startswith(f"{group}/{name}/{subject}/") and not f.endswith('/')]
            
            if len(files) != expected_count:
                errors.append(f"Expected {expected_count} files, found {len(files)}")
            
    except Exception as e:
        errors.append(str(e))
    
    return len(errors) == 0, errors