import io
import os.path

import yaml
from sphinx.util.osutil import ensuredir


def create_directory(app):
    ''' Creates the yaml directory if necessary '''
    app.env.yaml_dir = os.path.join(app.builder.confdir, '_build', 'yaml')
    ensuredir(app.env.yaml_dir)


def file_path(env, name):
    ''' Creates complete yaml file path for a name '''
    return os.path.join(
        env.yaml_dir,
        name if name.endswith('.yaml') else (name + '.yaml')
    )


def write(file_path, data_dict):
    ''' Writes dictionary into a yaml file '''
    with io.open(file_path, 'w', encoding='utf-8') as f:
        out = yaml.safe_dump(
            data_dict,
            default_flow_style=False,
            allow_unicode=True
        )
        f.write(out.decode('utf-8') if hasattr(out, 'decode') else out)


def read(file_path):
    ''' Reads dictionary from a yaml file '''
    with io.open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f.read())

