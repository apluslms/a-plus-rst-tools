import os.path
import yaml
from sphinx.util.osutil import ensuredir


def create_directory(app):
    ''' Creates the yaml directory if necessary '''
    app.env.yaml_dir = os.path.join(app.builder.outdir, '_yaml')
    ensuredir(app.env.yaml_dir)


def write(env, name, data_dict):
    ''' Writes dictionary into a yaml file '''
    path = os.path.join(
        env.yaml_dir,
        name if name.endswith('.yaml') else (name + '.yaml')
    )
    with open(path, 'w') as f:
        f.write(yaml.dump(data_dict, default_flow_style=False))
