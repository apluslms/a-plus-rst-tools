import os.path
import yaml
from sphinx.util.osutil import ensuredir


def create_directory(app):
    ''' Creates the yaml directory if necessary '''
    app.env.yaml_dir = os.path.join(app.builder.outdir, '_yaml')
    ensuredir(app.env.yaml_dir)


class YamlData:
    ''' Stores data to write into a yaml file. '''

    def __init__(self, env, file_name, data_dict):
        self.file = os.path.join(
            env.yaml_dir,
            file_name if file_name.endswith('.yaml') else (file_name + '.yaml')
        )
        self.data = data_dict

    def write(self):
        ''' Writes dictionary into a yaml file '''
        with open(self.file, 'w') as f:
            f.write(yaml.dump(self.data, default_flow_style=False))
