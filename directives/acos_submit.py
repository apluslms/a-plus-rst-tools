# -*- coding: utf-8 -*-
"""
acos-submit is a custom directive that behaves almost identically to the normal
submit directive. It is intended for exercises that are hosted outside the MOOC grader,
such as the ACOS server. The directive option url should define the URL path of
the exercise in the ACOS server. The URL domain is added automatically based on
the configuration value "acos_submit_base_url" (in conf.py). The acos-submit
directive also automatically uses the "ajax" flag of the submit directive.
"""
from sphinx.errors import SphinxError
from .submit import SubmitForm

class ACOSSubmitDirective(SubmitForm):
    def run(self):
        if 'config' in self.options:
            raise SphinxError('Do not use the "config" option with ACOS exercises.')
        if 'url' not in self.options:
            raise SphinxError('The "url" option is mandatory. ' \
                'It should only contain the URL path, not the domain, ' \
                'since the domain is read from the configuration value "acos_submit_base_url".')

        env = self.state.document.settings.env

        # modify some options before calling this method in the super class
        # ensure that the ajax option is set
        self.options['ajax'] = None # flag is active even though it is None in the docutils API

        # add the domain to the URL path
        self.options['url'] = env.config.acos_submit_base_url + self.options['url']

        # acos exercises don't need configuring
        self.options['no-configure'] = None

        return super().run()
