import os
from pathlib import Path
import yaml

class Config:
    def __init__(self, file: str):
        with open(file) as f:
            config_file: dict = yaml.safe_load(f)

        # username
        self.username = config_file.get('username')

        if not self.username:
            raise Exception('Missing config option: "username"')

        # password
        self.password = config_file.get('password')

        if not self.password:
            raise Exception('Missing config option: "password"')

        # staging
        self.staging = bool(config_file.get('staging'))

        # download location
        self.download_location = config_file.get('download_location') or os.path.join(Path.home(), 'Downloads')

        # company_id
        self.company_id = config_file.get('company_id')

        if not self.company_id:
            raise Exception('Missing config option: "company_id"')

        # project
        self.project_name = config_file.get('project_name')
        self.project_id = config_file.get('project_id')

        if not (self.project_name or self.project_id):
            raise Exception('Missing config option: "project_name" or "project_id"')

        # folders
        folders = config_file.get('folders') or []

        if not isinstance(folders, list):
            folders = [x for x in folders if x]
        else:
            folders = folders

        self.folders = [x for x in folders if x]

        # models
        models = config_file.get('models') or []

        if not isinstance(models, list):
            models = [models]
        else:
            models = models

        self.models = [x for x in models if x]

        # merged models
        merged_models = config_file.get('merged_models') or []

        if not isinstance(merged_models, list):
            merged_models = [merged_models]
        else:
            merged_models = merged_models

        self.merged_models = [x for x in merged_models if x]

        # dry run
        self.dry = config_file.get('dry') or False


if __name__ == "__main__":
    c = Config('configs/labc.yaml')
    pass
