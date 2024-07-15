import os
import sys
import threading
import shutil
import datetime
import requests

from loguru import logger

class InspectorUtils:
    def copyInspectResult(self, src_dir, dst_dir, notifyFunc) -> bool:
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
        return True

    def getProjectPath(self, xml_tree) -> str:
        if xml_tree is None:
            return ""
        try:
            root = xml_tree.getroot()
            project_element = root.find('project-name')
            if project_element is not None:
                project_name = os.path.basename(project_element.text)
                project_name = "/home/aoi/aoi/run/results/" + project_name
                logger.info(f"Get result project path: {project_name}")
            else:
                project_name = ""
                logger.error(f"Cannot find <project-name> element")
            return project_name
        except Exception as e:
            logger.error(f"Invalid xml document: {str(e)}")
        return ""
    
    def getSplitTimestamp(self) -> list[str]:
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f")[:-3]
        return timestamp.split("-")
    
    
    def sendResult(self, host, params) -> None:
        if host is None or host == "":
            return
        if params:
            url = host + "?" + '&'.join([f"{k}={v}" for k, v in params.items()])
        else:
            url = host
        logger.info(f"Request URL: {url}")
        response = requests.post(url)
        logger.warning(f"reponse status code: {response.status_code}")
        logger.warning(f"reponse content: {response.text}")
        
            
inspectorUtils = InspectorUtils()
        