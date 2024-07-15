import os
import sys
import threading
import shutil

from loguru import logger

class InspectorUtils:
    def copyResult(self, src_dir, dst_dir, notifyFunc) -> bool:
        if not os.path.exists(src_dir):
            logger.error(f"copyResult: {src_dir} not exists")
            return False
        
        if not os.path.exists(dst_dir):
            logger.info(f"copyResult: create dest dir: {dst_dir}")
            os.makedirs(dst_dir)

        total_files  = sum([len(files) for _, _, files in os.walk(src_dir)])
        copied_files = 0
        
        lock = threading.Lock()

        def copyCallback():
            nonlocal copied_files
            with lock:
                copied_files += 1
                if notifyFunc is not None:
                    notifyFunc(copied_files, total_files)
        
        def copyFunction(src_file, dst_file):
            logger.info(f"copyFunction: copy {src_file} to {dst_file}")
            shutil.copy2(src_file, dst_file)
            copyCallback()

        shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True, copy_function=copyFunction)

