import json
import os
import re
import subprocess
from datetime import date

INFO_PATH = f'info.json'
CHANGELOG_PATH = f'changelog.txt'

def version_as_str(version: tuple[int]) -> str:
    str_tuple = map(str, version)
    return '.'.join(str_tuple)

def str_as_version(version: str) -> tuple[int]:
    int_map = map(int, version.split('.'))
    return tuple(int_map)

def get_changelog_version() -> tuple[int]:
    version_regex = re.compile(r'Version: (?P<version>.*)$')
    with open(CHANGELOG_PATH, 'r', encoding='utf-8') as changelog:
        version_line = version_regex.match(changelog.read())
        version_str = version_line.group('version')
        return str_as_version(version_str)
    
def set_changelog_version(new_version):
    version_regex = re.compile(r'Version: (?P<version>.*)$')
    with open(CHANGELOG_PATH, 'r+', encoding='utf-8', newline='') as changelog:
        result = version_regex.sub(f'Version: {new_version}', changelog.read(), count=1)
        changelog.write(result)
    
def set_changelog_date():
    date_regex = re.compile(r'Date: (?P<date>.*)$')
    cur_date = date.today().isoformat() # YYYY-MM-DD
    with open(CHANGELOG_PATH, 'r+', encoding='utf-8', newline='') as changelog:
        result = date_regex.sub(f'Date: {cur_date}', changelog.read(), count=1)
        changelog.write(result)

def get_info_name() -> str:
    with open(INFO_PATH, 'r', encoding='utf-8', newline='') as info:
        parsed_info = json.load(info)
        version_str = parsed_info.get('name')
        return str_as_version(version_str) 

def get_info_version() -> tuple[int]:
    with open(INFO_PATH, 'r', encoding='utf-8', newline='') as info:
        parsed_info = json.load(info)
        version_str = parsed_info.get('version')
        return str_as_version(version_str)

def set_info_version(new_version: tuple[int]):
      new_version_str = version_as_str(new_version)
      with open(INFO_PATH, 'rw', encoding='utf-8', newline='') as info:
        parsed_info = json.load(info)
        old_version = parsed_info.get('version')
        result = info.read().replace(old_version, new_version_str)
        info.write(result)

def set_version_and_date():
    changelog_version = get_changelog_version()
    info_version = get_info_version()
    mod_version = version_as_str(max(changelog_version, info_version)) # Take the latest of the versions between changelog.txt and info.json
    if changelog_version > info_version:
        set_info_version(changelog_version)
    elif info_version > changelog_version: # they could be equal
        set_changelog_version(info_version)
    # Bump the latest date entry in the changelog
    set_changelog_date()
    # Commit will be done in yml so we store the name and version in the env file and exit
    env_path = os.getenv('GITHUB_ENV')
    with open(env_path, 'a') as env_file:
        env_file.write(f"MOD_NAME={get_info_name()}")
        env_file.write(f"MOD_VERSION={mod_version}")
        env_file.write(f"MOD_ZIP_PATH={get_info_name()}_{mod_version}.zip")
    
set_version_and_date()