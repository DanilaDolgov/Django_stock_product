from pathlib import Path
import os
import yaml


def open_file(file):
    with open(file, encoding='utf-8') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        return data


def file_data_yaml():
    my_files_import = []
    data_yaml_import = []
    path1 = os.path.join(Path(__file__).parents[1], 'data')
    [my_files_import.append(f'{path1}/{filename}') for filename in os.listdir(path1)]
    [data_yaml_import.append(open_file(file)) for file in my_files_import]
    return data_yaml_import
