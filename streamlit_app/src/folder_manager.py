import os
import json
import shutil
from datetime import datetime
import streamlit as st

class FolderManager:
    def __init__(self, base_path="projects"):
        self.base_path = base_path
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def create_project_structure(self, topic):
        """
        Creates the project folder structure:
        [Project_Name_Timestamp]/
        ├── input/
        ├── config/
        ├── images/
        └── output/
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join([c for c in topic if c.isalnum() or c in (' ', '_', '-')]).rstrip()
        project_name = f"{safe_topic.replace(' ', '_')}_{timestamp}"
        project_path = os.path.join(self.base_path, project_name)

        subfolders = ['input', 'config', 'images', 'output']
        for folder in subfolders:
            os.makedirs(os.path.join(project_path, folder), exist_ok=True)
        
        return project_path

    def save_uploaded_file(self, uploaded_file, target_folder):
        """Saves an uploaded file to the target folder."""
        if uploaded_file is None:
            return None
        
        file_path = os.path.join(target_folder, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path

    def load_json(self, file_path):
        """Loads JSON data from a file."""
        if not os.path.exists(file_path):
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_json(self, data, file_path):
        """Saves data to a JSON file."""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
