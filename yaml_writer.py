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
    with open(file_path, 'w') as f:
        f.write(yaml.dump(data_dict, default_flow_style=False))
