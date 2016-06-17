'''
Directive that places exercise submission forms.
'''
from docutils.parsers.rst import directives
from docutils import nodes
from directives.abstract_exercise import AbstractExercise
import aplus_nodes


translations = {
    'placeholder': {
        'en': 'A+ presents the exercise submission form here.',
        'fi': 'A+ esittää tässä kohdassa tehtävän palautuslomakkeen.',
    },
}


class SubmitForm(AbstractExercise):
    has_content = False
    option_spec = {
        'class' : directives.class_option,
        'submissions': directives.nonnegative_int,
        'points-to-pass': directives.nonnegative_int,
        'config': directives.unchanged,
        'url': directives.unchanged,
        'lti': directives.unchanged,
        'lti_context_id': directives.unchanged,
        'lti_resource_link_id': directives.unchanged,
    }

    def run(self):
        key, category, points = self.extract_exercise_arguments()

        env = self.state.document.settings.env
        name = env.docname.replace('/', '_') + '_' + key

        classes = ['exercise']
        if 'class' in self.options:
            classes.extend(self.options['class'])

        # Add document nodes.
        node = aplus_nodes.html('div', {
            'class': ' '.join(classes),
            'data-aplus-exercise': 'yes',
        })
        node.append(nodes.Text(translations['placeholder'][env.config['language'] or 'en']))

        # Try to load exercise configuration.
        if 'config' in self.options:
            print(self.options)

        # Store configuration.
        data = {
            'key': name,
            'category': category,
            'max_points': points,
            'max_submissions': self.options.get('submissions', env.config.program_default_submissions),
            'points_to_pass': self.options.get('points-to-pass', 0),
        }
        node.write_yaml(env, name, data, 'exercise')

        return [node]
