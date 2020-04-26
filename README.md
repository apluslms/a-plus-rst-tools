# A-plus RST tools

Provides tools to publish RST course content for mooc-grader and a-plus.

* http://www.sphinx-doc.org/en/stable/
* http://matplotlib.org/sampledoc/
* http://docutils.sourceforge.net/rst.html


## Creating a new course

We recommend to start with a fork from the [course-templates] repository
from Github.

    git clone --recursive https://github.com/apluslms/course-templates.git

Read the README in that repository in order to learn how to build and run
the course using Docker containers (recommended). If you do not use containers,
you need Python modules Sphinx and yaml in order to compile the RST source into
HTML and YAML course configuration files.

    pip install sphinx PyYAML

The course is compiled with make (when no containers are used).

    make html


## Adding tools to an existing course

The tools can be added into a repository as a submodule.

    git submodule add https://github.com/apluslms/a-plus-rst-tools.git a-plus-rst-tools
    git submodule init
    git submodule update

The course repository also needs certain configuration files for the RST tools
and Sphinx. The following files can be copied from the [course-templates] repository
to get started: apps.meta, conf.py, course.yml, docker-compile.sh, docker-compose.yml
and docker-up.sh. The course-templates README describes how to build and run
the course. The course directory should have a file index.rst that defines the
structure of the RST contents.

In order to build the course without any Docker containers, you install the
Python modules Sphinx and yaml as well as create the Sphinx configuration file
conf.py.

    pip install sphinx PyYAML
    sphinx-quickstart
    cp a-plus-rst-tools/conf.py .  # a similar conf.py is available in course-templates as well


[course-templates]: https://github.com/apluslms/course-templates


## Upgrading the tools

The tools can be upgraded to a newer version after the initial installation.
The command `git submodule update` updates or resets the submodule to the
version committed in the course repository.
It should be executed after a `git pull` if somebody has pushed a different
version of the submodule to the course repository. One can push the newest
version of the a-plus-rst-tools to the course repository by running
the following commands:

    cd my-course-repository  # start in the course repository
    cd a-plus-rst-tools
    git checkout master
    git pull
    cd ..  # to the course repository
    git add a-plus-rst-tools
    git commit -m 'Update a-plus-rst-tools'
    git push


## Special Sphinx configurations (conf.py)

The file conf.py in the root directory of the project is a configuration file
for the Sphinx RST compiler. The a-plus-rst-tools add some new configuration
values to the conf.py, for example, to define the course opening time.
The following Python snippet briefly shows these configurations.

```python
# -- Aplus configuration --------------------------------------------------
course_open_date = '2016-06-01'
course_close_date = '2020-06-06'
questionnaire_default_submissions = 5
program_default_submissions = 10
default_min_group_size = 1
default_max_group_size = 1
use_wide_column = True # should chapters use full or narrow column width?
static_host = os.environ.get('STATIC_CONTENT_HOST')

course_title = 'Basic course in programming' # can be defined in index.rst instead
submit_title = '{config_title}'
# submit_title: used when you need to modify the default structure of the titles
# in submit exercises. The string format keys config_title and key_title are available.
default_late_date = '2019-01-31 23:59' # default late close time for modules
default_late_penalty = 0.5 # default late penalty for modules

append_content = [] # Hack for modifying the YAML configuration at the end of the build.
# A list of file paths to YAML files that should be merged with the main index.yaml.
# This can add new keys or modify existing values in the index.
# The main index.yaml is built from the RST and YAML sources and contains
# all the modules, chapters, and exercises of the course.

override = {
    'submit': {
        'max_submissions': 99,
    },
}
# Hack for modifying exercise configurations based on category.
# The override dict uses category names as keys and the exercise configurations
# are updated at the end with the dict corresponding to the category.
# The category used is usually the hardcoded default (such as 'submit') instead
# of the manually set category.

category_names = {'submit': 'Programming exercises'}
# dict from category keys to category names
# This can be used to set visible category names if categories are set to
# exercises by keys.
static_host = 'http://localhost:8080/static/default'
# This overwrites the beginning of URLs in links to static materials.
# It is useful if the A+ frontend is otherwise unable to fix relative URLs
# in the contents that should refer to the backend server, not A+.

ae_default_submissions = 0 # default max submissions for active elements
skip_language_inconsistencies = False # for debugging multilanguage courses

# Default values for allow assistant viewing and grading settings in exercises
allow_assistant_viewing = True # May assistants view submissions?
allow_assistant_grading = False # May assistants grade submissions?
```

### Sphinx configurations that should be modified with a-plus-rst-tools

The Python modules that define Sphinx extensions (a setup function) must be
in the Python path (i.e., appended to the `sys.path`). At least the root of
the a-plus-rst-tools must be added, but the `aplus_setup` module does not
define all of the extensions available in the RST tools. The extensions
must be activated for Sphinx in the `extensions` list.

The RST tools defines a custom theme for the HTML builder and it must be activated
in the conf.py. The standard Sphinx themes produce HTML that does not work well
in A+ chapters.

The following settings are already defined in the template conf.py
(in the [course-templates]).

```python
sys.path.append(os.path.abspath('a-plus-rst-tools'))
sys.path.append(os.path.abspath('a-plus-rst-tools/directives'))

extensions = [
    'sphinx.ext.mathjax', # optional
    'aplus_setup',
]

html_theme = 'aplus'
html_theme_options = {
    'use_wide_column': use_wide_column,
}
html_theme_path = ['a-plus-rst-tools/theme']
```


## A+ course settings

Most A+ course settings can be set in the main index.rst of the course
(`master_doc` in conf.py) since A+ version 1.5, autumn 2019. The course settings
are defined as a field list **at the start of the index.rst file** before any section
(heading). Field lists are basically just key-value pairs (for background, see syntax in
[Docutils](http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#field-lists)
and [Sphinx](https://www.sphinx-doc.org/en/master/usage/restructuredtext/field-lists.html)).
The keys for the A+ course settings are listed below:

```rst
:course-start: 2019-08-01 12:00:00
:course-end: 2025-12-31 13:00:00
:course-default-late: 2026-06-01 15:00
:course-default-late-penalty: 0.60
:course-head-urls:
    - https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML
:course-description: <p>Description about the course for the course front page.</p>
    <p>More text.</p>
    <p>HTML formatting is allowed.</p>
:course-footer: <p>This is the course <b>footer</b> for the front page.</p>
:enrollment-start: 2019-09-01 11:00
:enrollment-end: 2020-01-01 12:00
:lifesupport-time: 2026-12-31 20:00
:archive-time: 2026-12-31 20:00
:view-content-to: enrolled
:enrollment-audience: internal
:index-mode: toc
:content-numbering: arabic
:module-numbering: arabic
:numerate-ignoring-modules: False
:questionnaire-default-reveal-model-at-max-submissions: False
:questionnaire-default-show-model: False
```

Some fields require a value from specific choices (see also
[the MOOC-grader documentation about the index.yaml file](https://github.com/apluslms/mooc-grader/blob/master/courses/README.md)):

* `view-content-to`: enrolled, enrollment_audience, all_registered, public
* `enrollment-audience`: internal, external, all
* `index-mode`: results, toc, last, experimental
* `content-numbering` and `module-numbering`: none, arabic, roman, hidden


## List of directives and examples

### 1. Graded questionnaire

The questionnaire directive arguments define the exercise key and optional max points
with the difficulty. For example, `.. questionnaire:: 1 A50` sets key `1`,
max points `50` and difficulty `A`. If not set in the directive arguments, the max points will be set to
the sum of the question points. Setting the difficulty is optional and it can be set
even if the max points aren't defined in the argument. The questionnaire directive accepts the following options:

* `submissions`: max submissions
* `points-to-pass`: points to pass
* `feedback`: If set, assumes the defaults for a feedback questionnaire
* `title`: exercise title
* `no-override`: If set, the conf.py override setting is ignored
* `pick_randomly`: integer. The questionnaire selects N questions randomly for
  the user instead of showing all questions. The random selection changes after
  the user submits, but persists without changes if the user just reloads the web page.
  (The questionnaire should not include any static text fields between the questions
  since the text fields are part of the pool from which the questions are randomly selected.)
* `preserve-questions-between-attempts`: If set, the questions in a `pick_randomly`
  questionnaire are preserved between submission attempts (instead of being
  resampled after each attempt).
* `category`: exercise category
* `status`: exercise status (default "unlisted"). See available [statuses](#list-of-exercise-statuses).
* `reveal-model-at-max-submissions`: The questionnaire feedback reveals
  the model solution after the user has consumed all submission attempts.
  The feedback may reveal the model solution even before the exercise deadline.
  Note that A+ has a separate feature for showing exercise model solutions after
  the deadline. Can be set to true or false. The default value can be set in
  index.rst with the field `questionnaire-default-reveal-model-at-max-submissions`.
  By default false.
* `show-model`: Students may open the model solution in A+ after the module
  deadline. Can be set to true or false. The default value can be set in
  index.rst with the field `questionnaire-default-show-model`. By default true.
* `allow-assistant-viewing`: Allows assistants to view the submissions of the students.
  Can be set to true or false. Overrides any options set in the conf.py or config.yaml files.
* `allow-assistant-grading`: Allows assistants to grade the submissions of the students.
  Can be set to true or false. Overrides any options set in the conf.py or config.yaml files.

The contents of the questionnaire directive define the questions and possible
instructions to students.

The **question directives** `pick-one`, `pick-any`, and `freetext` take the points
of the question as the first argument. If the questionnaire's max points are set, the sum
of the question points should be equal to them.
The question directives accept the following options:

* `class`: CSS class
* `required`: If set, the question is required and empty answers are rejected
* `key`: a manually set key for the question. This affects the HTML input element and
  the key in the submission data. If no key is set, note that automatically added
  keys change when the order and amount of questions is modified.

The `freetext` directive also accepts the following options in addition to
the common question options:

* `length`: (horizontal) length for the HTML text input
* `height`: If greater than 1, the textarea HTML element is used. Otherwise,
  a text input is used.
* Other options are defined in the code, but they mainly affect the CSS classes
  and they were implemented for very narrow usecases.

The `freetext` directive accepts a second positional argument after the points.
It defines the compare method for the model solution.
A textual input can be compared with the model solution as `int`, `float`,
`string`, `subdiff`, `regexp` or `unsortedchars` (unsorted character set).
The `regexp` compare method takes the correct answer as a regular
expression and tries to match the submission with it.
The `subdiff` method works almost like the `string` method, but it can have
multiple correct answers separated with `|` and if the answer is incorrect, it
shows the difference of the answer to each correct answer as a hint.
For example, when the correct answer is 'cat' and the student answers 'car',
the student receives feedback `Correct parts in your answer: ca-`.
String methods have comparison modifiers that are separated with a hyphen.
For example, `.. freetext:: 30 string-ignorews-ignorequotes`. The following
modifiers are available:

* `ignorews`: ignore white space (applies to regexp too)
* `ignorequotes`: iqnore "quotes" around
* `requirecase`: require identical lower and upper cases (only with the string
  and subdiff types)
* `ignorerepl`: ignore REPL prefixes
* `ignoreparenthesis`: ignore parenthesis "( )"

The question directives may define instructions. After the instructions,
the contents of the directive define the choices, the correct solution, and
possible hints. The hints are targeted to specific choices and they are shown
after answering. The format of the hints is `value § Feedback text`. The value
is the student's submission and it may be prepended with `!` in order to show
the feedback when the student did not answer that value. The special value
`%100%` shows the hint when the student answers the question correctly.
In freetext questions, the value may be prepended with `regexp:` in order to
use regular expressions for matching the student's submission.

Correct answers in `pick-one` and `pick-any` directives are marked with `*`.
A `pick-any` question may have neutral options, which are marked with `?`.
Neutral options are always counted as correct, whether the student selected them
or not. Initially selected options may be set with `+`. The initially selected
options are pre-selected when the exercise is loaded. The `+` character is
written before `*` or `?` if they are combined.

The `pick-any` directive has following options in addition to the common
question options:

* `partial-points`: When set, the question awards points for partially correct
  submissions. Zero points are awarded to answers that mark
  half or less of the options (checkboxes) correctly. The points scale linearly to
  the maximum points when more than half of the options are answered correctly.
* `randomized`: When this option is used, a subset of the answer choices (checkboxes)
  is randomly selected for the user. The random selection changes after the user
  submits, but persists when the user just reloads the web page. The value of
  the option is an integer, which is the number of choices to randomly select
  from all of the defined answer choices in the question. The option
  `correct-count` should be also set when this option is used.
* `correct-count`: The number of correct answer choices (checkboxes) to randomly
  select in the randomized `pick-any` question. This option is used with the
  `randomized` option.
* `preserve-questions-between-attempts`: If set, the answer choices in a `randomized`
  question are preserved between submission attempts (instead of being
  resampled after each attempt).

The `pick-one` questions are rendered with HTML radio buttons by default, but
a dropdown (select) element may be used with the `dropdown` option.

The body of the `freetext` question is
expected to be its model solution. However, the question instructions can be written
inside the body before the model answer. The instructions and the model solution must
be separated with an empty line.

If the questionnaire has the `feedback` option set, `freetext`
questions may not have a model solution and the body of the question is shown as the
question instructions.

```
.. questionnaire:: 1 A
  :submissions: 4
  :points-to-pass: 0

  This is a questionnaire with the key `1` that grants at maximum 70 points
  of difficulty A. Students can make at most 4 submissions.
  This exercise is marked passed when 0 points are reached (the default).

  .. pick-one:: 10
    :required:

    What is 1+1?

    a. 1
    *b. 2
    c. 3

    !b § Count again!
    b § That is correct!
    c § Too much

  (Hints can be included or omitted in any question.)

  .. pick-one:: 10
    :required:
    :dropdown:

    What is 1+2?

    +0. 0
    1. 1
    2. 2
    *3. 3

  .. pick-any:: 10
    :partial-points:

    Pick the two **first**. Since the 'partial-points' option is set,
    some points are awarded with a partially correct answer. If either one of the
    correct options is not chosen or one of the wrong fields is chosen, 5 points are
    still awarded. Selecting the last neutral option does not affect the points.

    +*a. this is the **first**
    *b. this is the **second**
    c. this is the **third**
    d. this is the **fourth**
    ?e. choosing this does not affect the granted points

  .. freetext:: 30 string-ignorews-ignorequotes-requirecase
    :length: 10

    A textual input can be compared with the model solution as integer, float or string.
    Here the correct answer is "test". Surrounding quotes are ignored in the solution
    as well as whitespace everywhere (modifiers ignorequotes and ignorews).

    test
    !test § Follow the instruction.
    regexp:Test|TEST § Use the lower case!

  .. freetext:: 10 regexp

    This question accepts either "red" or "blue" as the correct answer.
    The model solution is a regular expression.

    red|blue
```

### 2. Feedback questionnaire

A feedback questionnaire is almost like a graded questionnaire. When the
`feedback` option is set, the questionnaire uses the feedback category and
CSS class by default. Feedback questionnaires always grant full points if all
of the required questions are answered. The questionnaire options
`chapter-feedback`, `weekly-feedback`, `appendix-feedback`, and `course-feedback`
use a different CSS class (with the same name as the option).
If points are not specified, they are set to zero.
The `feedback` option can be set only to one questionnaire in an RST file because
the exercise key is then hardcoded to `feedback`.

The freetext questions are not expected to have a model solution, in essence the
body of the freetext question will be shown as the question instructions.

The question directives `agree-item` and `agree-item-generate` create questions
with a 1-5 Likert scale. They take a title as the only positional argument and
they accept the options `key`, `required`, and `class` like the other question
directives. `Agree-item-generate` also requires the option `config` that defines
the path to a config.yaml file. It is used to generate multiple agree items.
See the example below. (The agree item directives are quite limited and
you could just use the pick-one directive instead.)

Note that the [mooc-jutut service](https://github.com/Aalto-LeTech/mooc-jutut/)
provides a more advanced method for reading and responding to feedback.
In order to use it, you still define the feedback questionnaire in RST, but
you must also set the service URL of the questionnaire exercise to the mooc-jutut
server. The URL can be set by using the override option in the project conf.py
file. For example:

```python
override = {
    u'feedback': {
        u'url': u'https://jutut-server.org/feedback/coursekey/{key}',
    },
}
```

```
.. questionnaire::
  :feedback:

  Please fill in this feedback questionnaire.

  .. freetext::
    :required:
    :length: 100
    :height: 4
    :class: my-input-class

    What do you think now?

  .. agree-item:: Did it work for you?

  .. agree-item-generate:: Generated agree item with $title
    :config: path/to/config.yaml
```

The config.yaml file used by `agree-item-generate` may use the following keys:

```yaml
- title: My title 1
  info: Additional information 1 here
  image_url: http://localhost:8080/static/default/_images/myimage.png
- title: My title 2
  info: Additional information 2 here
  image_url: http://localhost:8080/static/default/_images/myimage.png
- title: My title 3
  info: Additional information 3 here
  image_url: http://localhost:8080/static/default/_images/myimage.png
```

### 3. Submittable exercise

These types of exercises are configured separately for the MOOC grader by
linking a YAML configuration file with the `config` option.
Some settings may also be defined directly with the directive options.
The directive will attach the exercise at this position in the content chapter.
Its arguments define the exercise key and max points with the optional difficulty.
The instructions can be written in the body of the submit directive. The body
supports RST syntax. If the instructions field is also given in the config.yaml, the
body of the submit directive will be prioritized.
It accepts the following options:

* `config`: path to the YAML configuration file
* `submissions`: max submissions
* `points-to-pass`: points to pass (default zero)
* `class`: CSS class(es)
* `title`: exercise title
* `category`: exercise category (default "submit")
* `status`: exercise status (default "unlisted"). See available [statuses](#list-of-exercise-statuses).
* `ajax`: If set, the A+ chapter does not attach any JavaScript event listeners
  to the exercise and the exercise JS may control the submission itself.
  See [the chapter content documentation](https://github.com/apluslms/a-plus/blob/master/doc/CONTENT.md)
  (the HTML attribute `data-aplus-ajax`).
* `allow-assistant-viewing`: Allows assistants to view the submissions of the students.
  Can be set to true or false. Overrides any options set in the conf.py or config.yaml files.
* `allow-assistant-grading`: Allows assistants to grade the submissions of the students.
  Can be set to true or false. Overrides any options set in the conf.py or config.yaml files.
* `quiz`: If set, the exercise feedback will take the place of the exercise instructions.
  This makes sense for questionnaires since their feedback contains the submission form.
  In RST, you would usually define questionnaires with the questionnaire directive,
  but they can also be defined in a YAML file.
  See [the chapter content documentation](https://github.com/apluslms/a-plus/blob/master/doc/CONTENT.md)
  (the HTML attribute `data-aplus-quiz`).
* `url`: the service URL of the exercise. Use this if the URL must, for example,
  refer to another server.
* `radar_tokenizer`: [See the Radar similarity analysis tool][Radar service]
* `radar_minimum_match_tokens`: [See the Radar similarity analysis tool][Radar service]
* `lti`: See LTI exercises in the next section. This option defines the label of
  the LTI service that must be configured in the A+ site beforehand.
* `lti_resource_link_id`: LTI exercise key
* `lti_context_id`: LTI course key
* `lti_open_in_iframe`: Open the exercise in an iframe inside the A+ page instead of a new window.
  This option does not take any parameters.
* `lti_aplus_get_and_post`: The exercise uses the A+ protocol to connect to the service.
  The LTI launch parameters are appended to the A+ protocol parameters. This does not work with standard LTI services.
  This option does not take any parameters.

[Radar service]: https://github.com/Aalto-LeTech/radar

```
.. submit:: 2 A100
  :submissions: 100
  :config: exercises/hello_python/config.yaml

  This will be shown in aplus as the instructions.
```

### 4. External exercise (LTI)

This exercise opens an external tool via the LTI launch protocol.
The LTI service must be configured beforehand in A+ by an administrator.
The `lti` option refers to the label of the LTI service.
The `url` option may exclude the domain of the service URL since the domain
must be equal to the URL defined in the LTI service anyway.
There are two ways to define LTI exercise:

* Using the config.yaml file linked with the `config` option and defining LTI options there.
  In this case, all LTI options written in the submit directive will be ignored.
* Writing LTI options in the submit directive. Remark that in this case the submit directive must
  not have the `config` option set.

In LTI excercises, the instructions cannot be written in the body of the submit directive.

```
.. submit:: 3 B50
  :lti: Rubyric
  :url: /aplus/123
  :lti_resource_link_id: example1
```

### 5. Meta (exercise round settings)

The aplusmeta directive is used to define module (exercise round) settings.
It should be defined in the RST file that defines the `toctree` of the module
(module index). Furthermore, it may be used in chapters to hide them (i.e., set status hidden)
with the `hidden` option or to set the chapter audience with the `audience` option.

The aplusmeta directive does not have any content and it accepts the following options:

* `open-time`: module open time, e.g., 2019-01-31 23:59:00 (the time defaults to 12:00 if excluded)
* `close-time`: module close time
* `late-time`: module late submission time
* `late-penalty`: module late penalty between 0-1, e.g., 0.5 (50%)
* `audience`: chapter audience (internal, external, or registered. Defaults to the course audience)
* `hidden`: If set, set status hidden for the module or chapter
* `points-to-pass`: module points to pass
* `introduction`: module introduction as an HTML string

Example module index.rst file:

```rst
Module 1 - Introduction
=======================

.. toctree::

  introduction
  topic

.. aplusmeta::
  :open-time: 2020-09-01 10:00
  :close-time: 2020-09-30 14:00
```

Alternatively, one can also define these options in the conf.py file of the
course in the following way.

1. Add the `aplusmeta_substitutions` variable in the conf.py file.

```python
    aplusmeta_substitutions = {
        'open01': '2020-09-10 10:01'
    }
```

This variable is a dictionary where keys are strings and values are dates
in the usual format (see above). In the example above, you have defined a
shortcut text "open01" for date "2020-09-10 10:01".

2. Use the shortcut texts in the aplusmeta directive in a module index.rst:

```rst
    .. aplusmeta::
      :open-time: open01
      :close-time: 2019-09-20 12:00
      :late-time: 2019-12-20 09:00
```

3. When the course is compiled, the aplusmeta directive looks for substitution
strings in the `aplusmeta_substitutions` dictionary. The substitutions can be
named freely as long as they are not RST markup (e.g. '|open01|' will not
work). The substitutions can be used with any option of the meta directive.


### 6. Active element input

This creates an input field for active element.

More active element examples can be found at https://version.aalto.fi/gitlab/piitulr1/active-element-example

Tools for making clickable active element inputs: https://version.aalto.fi/gitlab/piitulr1/click-input-editor

    .. ae-input:: id-for-input
      :title: title of the input (displayed on the html page)
      :default: default value for the input (displayed when the user has not
                submitted a solution)
      :class: Any css classes that the active element exercise div should have
              separated by a space (class1 class2 class3).
              In the example course css-file:
              - classes "active-element" and "ae-input" are used to style the
                input element and can be modified as needed.
              - classes "left" and "right" can be used to float the box left or
                right, or "center" to align it centered.
      :width: can be used to set the width of the element
      :height: can be used to set the height of the input textarea
               (default with classes "active element" and "ae-input" is 150px)
      :clear: "both" forces the element to a new line, "left" ("right") allows
              no floating elements on the left (right)
      :type: use "file" for file inputs, "clickable" for clickable inputs, and
             "dropdown" for dropdown. For dropdowns, the available options should
             be listed after the type indicating "dropdown" in this
             format: "dropdown:option1,option2,option3"
      :file: (only for type clickable) path to the html file that contains
             the default clickable input


### 7. Active element output

This creates an output field for active element.

More active element examples can be found at https://version.aalto.fi/gitlab/piitulr1/active-element-example

    .. ae-output:: key-for-output
      :config (required): path to the exercise configuration file
      :inputs (required): ids of the input elements required for the output
      :title: title of the output element
      :class: Any css classes that the active element exercise div should have
              separated by a space (class1 class2 class3).
              In the example css-file:
              - class "active-element" is used to style the
                input element and can be modified as needed.
              - classes "left" and "right" can be used to float the box left or
                right, or "center" to align it centered.
      :width: can be used to set the width of the element
      :height: can be used to set the height of the output div (default
               with class "active element" is 150px)
      :clear: "both" forces the element to a new line, "left" ("right") allows
              no floating elements on the left (right)
      :type: default type is text; for image (png) outputs use "image"
      :submissions: number of allowed submissions (default is unlimited for
                    active elements)
      :scale-size: no value; if this option is present, the output element
                   height will scale to match content that has a defined height
      :status: exercise status (default "unlisted"). See available [statuses](#list-of-exercise-statuses).

### 8. Hidden block

Directive for creating hidden content blocks. The content can be shown/hidden
by clicking the link. (This uses the Bootstrap collapse component.)

```
.. hidden-block:: name (required)
  :label: Optional text for the show/hide link (default Show/Hide)
  :visible: # if this flag is present, the collapsible div starts out visible

  Hidden content here.
```

### 9. Point of interest

Directive for creating a "point of interest" summary block.
This extension must be activated separately in the project conf.py
(`extensions = ["aplus_setup", "point_of_interest"]`).
A point of interest is mostly like a normal admonition ("coloured info box"), but
they are also linked to each other with next/previous links. The links enable
the user to quickly navigate between the points of interest.

Point of interests may also be used to generate separate lecture slides
(not directly included in the A+ content chapters). This requires a separate
tool called "presentation maker".

More information about [Columns and rows](#17-columns-and-rows).
```
.. point-of-interest:: Title text
  :id: unique id, if not supplied a random id will be generated
  :previous: id of previous point-of-interest (optional)
  :next: id of next point-of-interest (optional)
  :hidden: (if this flag is present, the content of this poi is hidden by default)
  :class: any additional css classes
  :height: fixed height in pixels
  :bgimg: path to background image
  :columns: relative widths of poi content columns (e.e. 2 3 3) Deprecated, since it is used with the newcol columns
  :not_in_slides: a flag used with the presentation maker. This POI does not show in the slides if this is defined.
  :not_in_book: If this flag is given, this POI does not appear in the A+ content chapter.
  :no_poi_box: Removes surrounding box and navigation

  Content of point-of-interest here.

  Use row and column directives to start a new row and column. More information about columns and rows in this documentation.
  Note: ::newcol columns are deprecated.

  .. row::

     .. column::
       :width: 6
       :column-class: bg-success

       Column content 1

     .. column::
       :width: 6
       :column-class: bg-warning

       Column content 2. Here goes the content.

```


### 10. Annotated code blocks

Code blocks may be annotated with comments for specific lines. This extension
must be activated separately in the project by adding the following settings to
the **conf.py** file located in the root of your course directory.

```python
extensions = ["aplus_setup", "annotated"]
...
include_annotated_js = True
include_annotated_css = True
```

This directive requires a custom JavaScript and CSS implementation for
highlighting the annotated code when the mouse hover events of the annotations
are fired in the web browser. Therefore, we have added a default implementation
that allow you to make use of the annotated directive without having to write
your own JS or CSS. However, if you want to remove the default JavaScript and
CSS implementation, you can change the value of `include_annotated_js` and
`include_annotated_css` to `False`. By doing so, you could write your own CSS
and JS code to interact with the annotated directive.

```
.. annotated::

  .. code-block:: python

    1«def func(param):»
        2«return None»

    3«x = "hello"»
    4«print(x + " world")»
    print("Last line without any annotation")

  Annotations may be written inline within text using square brackets (``[ ]``)
  or as blocks with the ``.. annotation::`` directive.
  Inline annotations look like this: [[[define a **function** named ``func`` that takes one parameter *param*]]].
  You can add a ``data-replacement`` attribute to the HTML code of the inline
  annotation too like this:
  [[[**return statement** ends the function execution and returns a value to the caller¶content for the replacement attribute]]]

  It is up to your custom JavaScript code to do something with the data-replacement
  attribute, but the intended use-case is that the content of the annotated code
  would change when the user hovers over the annotation with the mouse.

  The inline annotations are always numbered before the block annotations.
  This affects the numbers in the annotated code block
  (the sections like ``1«def func(param):»``).

  .. annotation:: optional content for the data-replacement HTML attribute

    Assign a string to the variable x.

  .. annotation::

    The parameters to the function call are evaluated first.
```

### 11. Code blocks with line references

With the `lineref-code-block`, you may add links from the chapter contents to
specific lines of the code block. You define labels enclosed in `::` for lines
of the code block. Labels can include alphanumeric characters, underscore (_),
and hyphen (-). The directive is used similarly to the Sphinx directive `code-block`.
This extension must be activated separately in the project conf.py
(`extensions = ["aplus_setup", "codeblock_lineref"]`).

```
.. lineref-code-block:: python
  :linenos:

  def example():
      :my-label-name:var = "something"
      return var

The role lref makes it possible to link to labels defined in lineref-code-block blocks:
:lref:`optional link text <my-label-name>`.
```

### 12. REPL sessions

The `repl` directive is used to print a (Scala) REPL session (read-eval-print loop).
This extension must be activated separately in the project conf.py
(`extensions = ["aplus_setup", "repl"]`).

```
.. repl-res-count-reset::

.. repl::

  > val numbers = List(1, 5, 6, 2)

  numbers: List[Int] = List(1, 5, 6, 2)
  > numbers.sum

  res0: Int = 14
```

### 13. Submittable ACOS exercises

The custom directive acos-submit behaves almost identically to the normal
submit directive. It is intended for exercises that are hosted outside the MOOC grader,
such as the ACOS server. The directive option url should define the URL path of
the exercise in the ACOS server. The URL domain is added automatically based on
the configuration value `acos_submit_base_url` in conf.py. The acos-submit
directive also automatically uses the `ajax` flag of the submit directive.

The usage:

```
In conf.py:
  acos_submit_base_url = 'https://acos.cs.aalto.fi'
  acos_submit_base_url = 'http://172.21.0.4:3000'

In RST:
.. acos-submit:: somekey 100
  :title: My title
  :url: /aplus/draganddrop/draganddrop-example/revealdemo
```

### 14. HTML div elements

The div directive can be used to insert basic `<div>` html elements into the
generated document. This is useful for styling and other similar reasons.

Any arguments given to the directive will be added as classes to the resulting
element.

This extension is originally from
https://github.com/dnnsoftware/Docs/blob/master/common/ext/div.py
and is licensed under the MIT license (see source file comments for the
license text).

Usage example:

```
.. div:: css-class-1 css-class-2

  Element contents (_parsed_ as **RST**). Note the blank line and the
  indentation.
```

### 15. CSS styled topics

Directive that inserts `topic` elements that are more friendly to css styling
using the bootstrap framework. Usage:

```
.. styled-topic::
  :class: css-class-1 css-class-2

  Topic must include content. All content is **parsed** _normally_ as RST.

  Note the blank line between the directive and its content, and the
  indentation.
```

An optional `:class:` option can be used to insert other css classes to the
resulting `<div>` element.

This extension also registers a conf.py value of
`'bootstrap_styled_topic_classes'`. It can be used to set default classes that are
added to all styled-topic directives. The default value is `dl-horizontal topic`
where `dl-horizontal` is useful for inserting bootstrap styled `<dl>` elements
into the div.

### 16. Media directives

The media directives were developed basically for a single course and they
may not be quite reusable for other usecases, but they are listed here anyway.
This extension must be activated separately in the project conf.py
(`extensions = ["aplus_setup", "media"]`).

**A story embedded in an iframe.**

```
.. story:: story_name
  :story-height: 690
  :story-width: 865
```

**JSVee program visualization (hosted in the MOOC grader).**
This requires a JavaScript library obtained elsewhere.

```
.. jsvee:: id
```

**YouTube video**

```
.. youtube:: id
  :video-height: 400
  :video-width: 640
```

**Local video** hosted in the `_static/videot` directory of the course in
the mp4 or webm format. The id argument is the filename without the extension.

```
.. local-video:: id
  :video-width: 650
```

**Embedded page (iframe)**

```
.. embedded-page:: url
  :frame-height: 500
  :frame-width: 850
```

### 17. Columns and rows

Directive for creating columns and rows. Primarily designed to be used with "point of interest" summary blocks. But should also work independently to layout content.

This extension must be activated separately in the project conf.py (extensions = ["aplus_setup", "row"]).

**Note**

Column (`:columns:`) options in the point of interest directive do not work with these columns. Use it with the columns created with `::newcol`.

```
Example with point-of-interest directive.

Available options:
:width: sets column width. Maximum value of 12 when using one column. If not set it will use full width (12).
:column-class: Bootstrap classes can be applied. See example below.


.. point-of-interest:: Test

   .. row::

     .. column::
       :width: 8
       :column-class: bg-warning text-center

       .col-8 this is column's content.

       .. row::

         .. column::
           :width: 6
           :column-class: bg-light

           .col-6

         .. column::
           :width: 6
           :column-class: bg-secondary

           .col-6

     .. column::
       :width: 4
       :column-class: bg-success

       .col-4

```
Width is not mandatory, but if it is not given then it uses the width of 12 automatically.

**Note - newcol is deprecated**

Older columns (`::newcol`) work, but they are deprecated. Column and row directives should be used instead.

### 18. Tabs

The `rst-tabs` directive is designed to add tabbed content. Tabs separate content into different panels so that one
panel is displayed at a time.

The following snippet of code is an example on how you can use `rst-tabs` directive. As you can see in the example,
the `rst-tabs` directive can contain one or more `tab-content` directives. Each `tab-content` requires one argument,
which is used internally to identify individual `tab-content`. Therefore, this argument must be unique and cannot contain
any whitespace. You must also add the option `title` to the `tab-content` directive since it is the title that will be shown
in your tabs. The content of each `tab-content` can be any RST directive.

```rst

.. rst-tabs::

  .. tab-content:: tab-html-render
    :title: HTML visualisation

    .. raw:: html

      <h1>Title</h1>

    :menuselection:`Action 1 --> Action 2`

    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus hendrerit
    auctor quam at maximus. Phasellus ornare suscipit tortor et aliquet. Aliquam
    erat volutpat. Aliquam at orci vel nibh tincidunt lacinia. Cras gravida,
    mauris eget vulputate ullamcorper, turpis est commodo velit, consequat
    pulvinar augue mi malesuada metus. Maecenas ac diam et augue placerat
    faucibus. Nullam ut iaculis nisi.

  .. tab-content:: tab-code
    :title: RST Code

    .. code-block:: rst

      Title
      =====

      :menuselection:`Action 1 --> Action 2`

      Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus hendrerit
      auctor quam at maximus. Phasellus ornare suscipit tortor et aliquet. Aliquam
      erat volutpat. Aliquam at orci vel nibh tincidunt lacinia. Cras gravida,
      mauris eget vulputate ullamcorper, turpis est commodo velit, consequat
      pulvinar augue mi malesuada metus. Maecenas ac diam et augue placerat
      faucibus. Nullam ut iaculis nisi.
```

### List of exercise statuses

There are 6 possible statuses for exercises:

* ready: Visible exercise listed in table of contents.
* unlisted (default): Unlisted in table of contents, otherwise same as ready.
* hidden: Hidden from non course staff.
* enrollment: Questions for students when they enroll to a course.
* enrollment_ext: Same as enrollment but for external students.
* maintenance: Hides the exercise description and prevents submissions.
