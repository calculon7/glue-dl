# glue-dl.py v1.0

import os
import re
from datetime import datetime
from time import sleep
from urllib.parse import quote, unquote
from pathlib import Path
import requests
import db


def quote_gluestring(s: str):
    s = quote(s)
    s = s.replace(quote(' '), '+')

    return s

def unquote_gluestring(s: str):
    s = s.replace('+', ' ')
    s = unquote(s)

    return s


class Glue():
    base_url_b2: str
    base_url_b4: str
    base_url_accounts: str

    session = requests.session()
    username = None
    is_logged_in = False
    hostname = None

    def __init__(self, staging=False):
        if staging:
            self.base_url_b2 = 'b2-staging.autodesk.com'
            self.base_url_b4 = 'b4-staging.autodesk.com'
            self.base_url_accounts = 'accounts-staging.autodesk.com'
        else:
            self.base_url_b2 = 'b2.autodesk.com'
            self.base_url_b4 = 'b4.autodesk.com'
            self.base_url_accounts = 'accounts.autodesk.com'

    def login(self, username, password):
        self.username = None
        self.hostname = None
        self.is_logged_in = False

        # login page
        page_res = self.session.get(f'https://{self.base_url_b2}/login')
        page_res.raise_for_status()

        # click login
        login_res = self.session.get(f'https://{self.base_url_b2}/consumer?openid_identifier=https://{self.base_url_accounts}&inIFrame=1')
        login_res.raise_for_status()

        auth_key = re.search(r'AuthKey%3D([a-z0-9-]+)"', login_res.text)[1]
        token = re.search(r'name="__RequestVerificationToken" type="hidden" value="([^"]+)"', login_res.text)[1]

        # submit username
        username_res = self.session.post(
            f'https://{self.base_url_accounts}/Authentication/IsExistingUser?viewmode=iframe&ReturnUrl=%2Fauthorize%3Fviewmode%3Diframe%26lang%3Den-US%26realm%3D{self.base_url_b2}%26ctx%3Dbim360w%26AuthKey%3D' + auth_key,
            data={
                '__RequestVerificationToken': token,
                'UserName': username,
            }
        )
        username_res.raise_for_status()

        # submit password
        pw_res = self.session.post(
            f'https://{self.base_url_accounts}/Authentication/LogOn?viewmode=iframe&ReturnUrl=%2Fauthorize%3Fviewmode%3Diframe%26lang%3Den-US%26realm%3D{self.base_url_b2}%26ctx%3Dbim360w%26AuthKey%3D' + auth_key,
            data={
                "__RequestVerificationToken": token,
                "queryStrings": f"?viewmode=iframe&ReturnUrl=%2Fauthorize%3Fviewmode%3Diframe%26lang%3Den-US%26realm%3D{self.base_url_b2}%26ctx%3Dbim360w%26AuthKey%3D" + auth_key,
                "signinThrottledMessage": "You+have+made+too+many+sign+in+attempts+recently.+Please+try+again+later.",
                "UserName": username,
                "Password": password,
                "RememberMe": "false"
            }
        )
        pw_res.raise_for_status()

        # finalize auth
        auth_res = self.session.post(
            f'https://{self.base_url_b2}/consumer?is_return=true&isIFrame=true',
            data={
                "openid.claimed_id":            re.search(r'<input type="hidden" name="openid.claimed_id" value="([^"]*)" />',           pw_res.text)[1],
                "openid.identity":              re.search(r'<input type="hidden" name="openid.identity" value="([^"]*)" />',             pw_res.text)[1],
                "openid.sig":                   re.search(r'<input type="hidden" name="openid.sig" value="([^"]*)" />',                  pw_res.text)[1],
                "openid.signed":                re.search(r'<input type="hidden" name="openid.signed" value="([^"]*)" />',               pw_res.text)[1],
                "openid.assoc_handle":          re.search(r'<input type="hidden" name="openid.assoc_handle" value="([^"]*)" />',         pw_res.text)[1],
                "openid.op_endpoint":           re.search(r'<input type="hidden" name="openid.op_endpoint" value="([^"]*)" />',          pw_res.text)[1],
                "openid.return_to":             re.search(r'<input type="hidden" name="openid.return_to" value="([^"]*)" />',            pw_res.text)[1].replace('&amp;', '&'), # could use html.unescape
                "openid.response_nonce":        re.search(r'<input type="hidden" name="openid.response_nonce" value="([^"]*)" />',       pw_res.text)[1],
                "openid.mode":                  re.search(r'<input type="hidden" name="openid.mode" value="([^"]*)" />',                 pw_res.text)[1],
                "openid.ns":                    re.search(r'<input type="hidden" name="openid.ns" value="([^"]*)" />',                   pw_res.text)[1],
                "openid.ns.alias3":             re.search(r'<input type="hidden" name="openid.ns.alias3" value="([^"]*)" />',            pw_res.text)[1],
                "openid.alias3.request_token":  re.search(r'<input type="hidden" name="openid.alias3.request_token" value="([^"]*)" />', pw_res.text)[1],
                "openid.alias3.scope":          re.search(r'<input type="hidden" name="openid.alias3.scope" value="([^"]*)" />',         pw_res.text)[1],
                "openid.ns.alias4":             re.search(r'<input type="hidden" name="openid.ns.alias4" value="([^"]*)" />',            pw_res.text)[1],
                "openid.alias4.mode":           re.search(r'<input type="hidden" name="openid.alias4.mode" value="([^"]*)" />',          pw_res.text)[1],
                "openid.alias4.type.alias1":    re.search(r'<input type="hidden" name="openid.alias4.type.alias1" value="([^"]*)" />',   pw_res.text)[1],
                "openid.alias4.value.alias1":   re.search(r'<input type="hidden" name="openid.alias4.value.alias1" value="([^"]*)" />',  pw_res.text)[1],
                "openid.alias4.type.alias2":    re.search(r'<input type="hidden" name="openid.alias4.type.alias2" value="([^"]*)" />',   pw_res.text)[1],
                "openid.alias4.value.alias2":   re.search(r'<input type="hidden" name="openid.alias4.value.alias2" value="([^"]*)" />',  pw_res.text)[1],
                "openid.alias4.type.alias3":    re.search(r'<input type="hidden" name="openid.alias4.type.alias3" value="([^"]*)" />',   pw_res.text)[1],
                "openid.alias4.value.alias3":   re.search(r'<input type="hidden" name="openid.alias4.value.alias3" value="([^"]*)" />',  pw_res.text)[1],
                "openid.alias4.type.alias4":    re.search(r'<input type="hidden" name="openid.alias4.type.alias4" value="([^"]*)" />',   pw_res.text)[1],
                "openid.alias4.value.alias4":   re.search(r'<input type="hidden" name="openid.alias4.value.alias4" value="([^"]*)" />',  pw_res.text)[1],
                "openid.alias4.type.alias5":    re.search(r'<input type="hidden" name="openid.alias4.type.alias5" value="([^"]*)" />',   pw_res.text)[1],
                "openid.alias4.value.alias5":   re.search(r'<input type="hidden" name="openid.alias4.value.alias5" value="([^"]*)" />',  pw_res.text)[1],
            }
        )
        auth_res.raise_for_status()

        if not (auth_res.cookies.get('g_id') and auth_res.cookies.get('g_s') and auth_res.cookies.get('oi_oid')):
            raise Exception('Could not login')

        self.username = username
        self.is_logged_in = True

    def get_host_listing(self) -> dict:
        assert self.is_logged_in

        res = self.session.get(f'https://{self.base_url_b2}/GlueApiServlet?api=getHostListing',
            headers={
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'https://{self.base_url_b2}/access'
        })

        res.raise_for_status()
        return res.json()

    def connect_to_host(self, hostname):
        self.hostname = None

        if self.session.cookies.get('g_as'):
            self.session.cookies.clear(self.base_url_b2, '/', 'g_as') # pylint: disable=too-many-function-args

        if self.session.cookies.get('g_h'):
            self.session.cookies.clear(self.base_url_b2, '/', 'g_h') # pylint: disable=too-many-function-args

        res = self.session.get(f'https://{self.base_url_b2}/GlueHostServlet?host=' + hostname,
            headers={
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'https://{self.base_url_b2}/host'
        })

        res.raise_for_status()
        assert self.session.cookies.get('g_as')
        assert self.session.cookies.get('g_h')

        self.hostname = hostname

    def get_user_info(self) -> dict:
        assert self.hostname

        res = self.session.get(f'https://{self.base_url_b2}/GlueApiServlet?api=api%2Fuser%2Fv1%2Finfo.json',
            headers={
                'Referer': f'https://{self.base_url_b2}/',
                'X-Requested-With': 'XMLHttpRequest',
        })

        res.raise_for_status()
        return res.json()

    def get_signature(self) -> dict:
        '''Response can be used with offical API endpoints. Must be logged into host before calling.'''

        assert self.hostname

        res = self.session.get(f'https://{self.base_url_b2}/GlueApiServlet?api=getSignature', headers={
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'https://{self.base_url_b2}/i/{self.hostname}'
        })

        res.raise_for_status()
        return res.json()

    def get_project_listing(self) -> dict:
        assert self.hostname

        res = self.session.get(f'https://{self.base_url_b2}/GlueApiServlet?api=api%2Fproject%2Fv1%2Flist.json&page_size=100&page=1', headers={
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'https://{self.base_url_b2}/i/' + self.hostname
        })

        res.raise_for_status()
        return res.json()

    def get_project_info(self, project_id, depth=0, lightweight=True) -> dict:
        '''change depth for detailed folder tree'''

        res = self.session.get(f'https://{self.base_url_b2}/GlueApiServlet?api=api%2Fproject%2Fv1%2Finfo.json&lightweight={int(lightweight)}&depth={depth}&project_id={project_id}', 
        headers={
            'Referer': f'https:/{self.base_url_b2}/i/{self.hostname}',
            'X-Requested-With': 'XMLHttpRequest',
        })

        res.raise_for_status()
        return res.json()

    def get_project_tree(self, company_id, project_id, folder_id=None, depth=None, lightweight=True, get_folder_structure=False, get_basic_info_only=False) -> dict:
        assert self.hostname

        sig = self.get_signature()

        res = self.session.get(f'https://{self.base_url_b4}:443/api/project/v1/tree.json', 
            params={
                'company_id':   company_id,
                'api_key':      sig['publicKey'],
                'auth_token':   sig['authToken'],
                'timestamp':    sig['timestamp'],
                'sig':          sig['signature'],
                'project_id': project_id,
                'depth': depth,
                'folder_id': folder_id,
                'lightweight': int(lightweight),
                'get_folder_structure': int(get_folder_structure),
                'get_basic_info_only': int(get_basic_info_only),
            },
            headers={
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'https://{self.base_url_b2}/i/{self.hostname}/{project_id}'
            }
        )

        res.raise_for_status()
        return res.json()

    def get_model_listing(self, company_guid, project_id, merged=False, folder_id=None, exclude_deleted=True) -> dict:
        model_type = 'merged_models' if merged else 'single_models'

        res = self.session.get(f'https://{self.base_url_b2}/GlueApiServlet', 
            params={
                'api': f'api%2Fv3%2Faccounts%2F{company_guid}%2Fprojects%2F{project_id}%2F{model_type}',
                'limit': 99999,
                'exclude_deleted': int(exclude_deleted),
                'filter': f"parent_folder_id eq '{folder_id}'" if folder_id else None,
            }, 
            headers={
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'https://{self.base_url_b2}/i/{self.hostname}/{project_id}'
        })

        res.raise_for_status()
        return res.json()

    def get_model_info(self, model_id, lightweight=True) -> dict:
        res = self.session.get(f'https://{self.base_url_b2}/GlueApiServlet?api=api%2Fmodel%2Fv2%2Finfo.json&model_id={model_id}&lightweight={int(lightweight)}', 
            headers={
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'https://{self.base_url_b2}/i/{self.hostname}'
        })

        res.raise_for_status()
        return res.json()

    def aggregate_model(self, company_id, model_id) -> dict:
        # can only aggregate merged model
        sig = self.get_signature()

        res = self.session.post(f'https://{self.base_url_b4}:443/api/model/v1/aggregate.json', data={
            'company_id':   company_id,
            'api_key':      sig['publicKey'],
            'auth_token':   sig['authToken'],
            'timestamp':    sig['timestamp'],
            'sig':          sig['signature'],
            'model_id':     model_id,
        })

        res.raise_for_status()
        body = res.json()
        assert body['status'] == 'WAITING'
        
        return body

    def wait_until_model_parsed(self, model_id, interval=15, timeout=600) -> int:
        time_waited = 0

        while self.get_model_info(model_id)['file_parsed_status'] == 0:
            if time_waited >= timeout:
                raise TimeoutError

            sleep(interval)
            time_waited += interval

        return time_waited

    def download_model(self, company_id, model_id, filepath, nwd=False) -> bool:
        # If you perform a HEAD operation, you will only receive the header with the Content-Length set to the length of the model file.
        # merged models must be downloaded as nwds
        # merged models that have not been parsed yet will download an empty text file

        model_info = self.get_model_info(model_id)

        # merged models must be downloaded as nwd
        if model_info['is_merged_model'] == 1:
            nwd = True

        # if file not parsed on glue
        if nwd and model_info['file_parsed_status'] == 0:
            
            # request parsing if merged model
            if model_info['is_merged_model'] == 1:
                self.aggregate_model(company_id, model_id)

            self.wait_until_model_parsed(model_id)
        
        sig = self.get_signature()

        dl_start_time = datetime.now()

        # download file
        res = self.session.get(f'https://{self.base_url_b4}:443/api/model/v1/download', stream=True, params={
            'company_id':   company_id,
            'api_key':      sig['publicKey'],
            'auth_token':   sig['authToken'],
            'timestamp':    sig['timestamp'],
            'sig':          sig['signature'],
            'model_id':     model_id,
            'alt_format':   'nwd' if nwd else '', # .nwd files will automatically be downloaded as nwd
        })

        res.raise_for_status()

        # create download directory if it does not exist
        file_dir = Path(filepath).parent
        if not os.path.isdir(file_dir):
            os.mkdir(file_dir)

        with open(filepath, 'wb') as f:
            for chunk in res.iter_content(chunk_size=4096):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)


        # check if download successful
        file_exists = os.path.isfile(filepath)

        if file_exists:
            file_modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            file_is_new = file_modified_time > dl_start_time
            return file_is_new
        else:
            return False

    def get_project_user_notification_settings(self, project_id) -> dict:
        res = self.session.get(f'https://{self.base_url_b2}/GlueApiServlet',
            params = {
                'api': 'api/project/v1/user/notification/get_settings.json',
                'project_id': project_id,
            },
            headers = {
                'Referer': f'https://{self.base_url_b2}/',
                'X-Requested-With': 'XMLHttpRequest',
            }
        )
        
        res.raise_for_status()

        return res.json()

    def set_project_user_notification_settings(self, project_id, nsettings):
        res = self.session.post(f'https://{self.base_url_b2}/GlueApiServlet',
            data={
                'api': 'api/project/v1/user/notification/set_settings.json',
                'project_id': project_id,
                'nsettings': nsettings,  # "model;mergedmodel;"
            },
            headers = {
                'Referer': f'https://{self.base_url_b2}/',
                'X-Requested-With': 'XMLHttpRequest',
            }
        )

        res.raise_for_status()

        return res.json()

    def find_folder(self, company_id, project_id, folder_name):
        def __search_folder_contents_recursive(folder_contents: dict, target_folder_name: str):
            for subfolder in folder_contents:
                subfolder_name = unquote_gluestring(subfolder['name'])

                if subfolder_name == target_folder_name:
                    return subfolder

                else:
                    if 'folder_contents' in subfolder:
                        sub_found = __search_folder_contents_recursive(subfolder['folder_contents'], target_folder_name)

                        if sub_found:
                            return sub_found

            return None

        tree = self.get_project_tree(company_id, project_id, get_folder_structure=True)['folder_only_structure']
        models_tree = next((x for x in tree if x['name'] == 'Models'), None)

        return __search_folder_contents_recursive(models_tree['folder_contents'], folder_name)

    # TODO should not use db class if in Glue class
    # TODO repeat download code
    def download_folder(self, _company_id, _project_id, _project_name, folder_id, _download_location, dry) -> None:
        folder_contents = self.get_project_tree(_company_id, _project_id, folder_id)['folder_tree'][0].get('folder_contents')

        if not folder_contents:
            return

        for content in folder_contents:
            if content['type'] == 'MODEL':
                model_info = self.get_model_info(content['object_id'])

                if db.file_is_new(_company_id, _project_name, model_info):
                    _filepath = os.path.join(_download_location, unquote_gluestring(model_info['model_name']))

                    if dry:
                        _success = True
                    else:
                        _success = self.download_model(_company_id, model_info['model_id'], _filepath)

                    if _success:
                        db.update(_company_id, _project_name, model_info['model_id'], model_info['model_name'], model_info['model_version'])
                        print(f'Downloaded: {model_info["model_name"]}')

                    else:
                        print(f'Error: file download {model_info["model_name"]} failed')

                else:
                    print(f'Skipped: {model_info["model_name"]}')

            elif content['type'] == 'FOLDER':
                self.download_folder(_company_id, _project_id, _project_name, content['object_id'], _download_location, dry)


    def get_company(self, company_id):
        host_list = self.get_host_listing()['list']

        company_match = next((x for x in host_list if x['company_id'] == company_id), None)

        if not company_match:
            print(f'company_id {company_match["company_id"]} not found')
            exit(2)
        
        company = Company()
        company.company_id = company_id
        company.company_guid = company_match['company_guid']

        return company
        
    def get_project(self, project_name):
        project_list = self.get_project_listing()['project_list']

        project_match = next((x for x in project_list if x['project_name'] == project_name), None)

        if not project_match:
            print(f'project_name {project_match["project_name"]} not found for hostname {self.hostname}')
            exit(3)

        project = Project()
        project.project_name = project_name
        project.project_id = project_match["project_id"]

        return project


class Company:
    company_id: str
    company_guid: str


class Project:
    project_id: str
    project_name: str
