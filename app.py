import os
import sys
import db
from glue import Glue, unquote_gluestring
from config import Config
import re


if len(sys.argv) < 2:
    print('No config file provided')
    exit(1)

cfg = Config(sys.argv[1])

glue = Glue(staging=cfg.staging)
glue.login(cfg.username, cfg.password)

glue.connect_to_host(cfg.company_id)
company = glue.get_company(cfg.company_id)
project = glue.get_project(cfg.project_name)

if cfg.dry:
    print('Info: dry run enabled')

# get project notification settings
project_settings = glue.get_project_user_notification_settings(project.project_id)

notification_settings = ';'.join([x for x in project_settings['notification_settings'] if project_settings['notification_settings'][x] == '1'])

if notification_settings == '':
    # nsettings is blank, it probably wasn't reset last time
    # turn on model notifications when finished
    notification_settings = 'model'
    print('Warning: all notifications off, enabling model notifications')

try:
    # turn off model notifications to prevent Glue from sending downloaded notification
    glue.set_project_user_notification_settings(project.project_id, '')

    if cfg.models:
        model_listing = glue.get_model_listing(company.company_guid, project.project_id)

        for model_name in cfg.models:
            model = next((x for x in model_listing if x['model_name'] == model_name), None)

            if model:
                if db.file_is_new(cfg.company_id, cfg.project_name, model):
                    filepath = os.path.join(cfg.download_location, unquote_gluestring(model['model_name']))

                    if cfg.dry:
                        success = True
                    else:
                        success = glue.download_model(cfg.company_id, model['model_id'], filepath)

                    if success:
                        db.update(cfg.company_id, cfg.project_name, model['model_id'], model['model_name'], model['model_version'])
                        print(f'Downloaded: {model["model_name"]}')

                    else:
                        print(f'Error: file download {model["model_name"]} failed')

                else:
                    print(f'Skipped: {model["model_name"]}')

            else:
                print(f'Error: model {model_name} not found')

    if cfg.folders:
        for folder_name in cfg.folders:
            guid_match = re.fullmatch(r'\w{8}-\w{4}-\w{4}-\w{4}-\w{12}', folder_name)  # type:ignore

            if guid_match:
                folder = glue.get_project_tree(cfg.company_id, project.project_id, folder_name)
                folder_id = folder_name

            else:
                folder = glue.find_folder(cfg.company_id, project.project_id, folder_name)
                folder_id = folder['object_id']

            if folder:
                glue.download_folder(cfg.company_id, project.project_id, cfg.project_name, folder_id, cfg.download_location, cfg.dry)

            else:
                print(f'Error: folder {folder_name} not found')

    if cfg.merged_models:
        merged_model_listing = glue.get_model_listing(company.company_guid, project.project_id, merged=True)

        for merged_model_name in cfg.merged_models:
            merged_model = next((x for x in merged_model_listing if x['model_name'] == merged_model_name), None)

            if merged_model:
                if db.file_is_new(cfg.company_id, cfg.project_name, merged_model):
                    filepath = os.path.join(cfg.download_location, unquote_gluestring(merged_model['model_name']) + '.nwd')

                    if cfg.dry:
                        success = True
                    else:
                        success = glue.download_model(cfg.company_id, merged_model['model_id'], filepath)

                    if success:
                        db.update(cfg.company_id, cfg.project_name, merged_model['model_id'], merged_model['model_name'], merged_model['model_version'])
                        print(f'Downloaded: {merged_model["model_name"]}')

                    else:
                        print(f'Error: file download {merged_model["model_name"]} failed')

                else:
                    print(f'Skipped: {merged_model["model_name"]}')

            else:
                print(f'Error: merged model {merged_model_name} not found')

finally:
    # turn back on original notifications
    glue.set_project_user_notification_settings(project.project_id, notification_settings)
