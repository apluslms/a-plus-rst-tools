# A-plus RST tools

Provides tools to publish RST course content for mooc-grader and a-plus.

* http://www.sphinx-doc.org/en/stable/
* http://matplotlib.org/sampledoc/
* http://docutils.sourceforge.net/rst.html

A-plus RST tools comprise a set of Sphinx extensions.
Sphinx is a tool for writing documentation mainly in the reStructuredText (RST) markup language,
though it also supports other markup languages such as markdown via extensions.
Sphinx itself extends the Docutils RST parser and compiler.
A-plus RST tools support the following Sphinx versions:

* a-plus-rst-tools v1.4 support Sphinx v4.1.
* a-plus-rst-tools v1.3 and earlier support Sphinx v1.6.

## Creating a new course

We recommend to start with a fork from the [course-templates] repository
from Github.

    git clone --recursive https://github.com/apluslms/aplus-course-template.git

Read the README in that repository in order to learn how to build and run
the course using Docker containers (recommended). If you do not use containers,
you need Python modules Sphinx and yaml in order to compile the RST source into
HTML and YAML course configuration files.

    pip install sphinx~=4.1.2 PyYAML~=5.4.1

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

    pip install sphinx~=4.1.2 PyYAML~=5.4.1
    sphinx-quickstart
    cp a-plus-rst-tools/conf.py .  # a similar conf.py is available in course-templates as well


[course-templates]: https://github.com/apluslms/aplus-course-template


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
course_key = os.environ.get('COURSE_KEY')
course_id = os.environ.get('COURSE_ID')

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

default_exercise_url = f"https://somedomain/{course_id}/{{key}}"
# Note that f"https://somedomain/{course_id}/{{key}}" directly evaluates to
# something like "https://somedomain/3/{key}".
# The default exercise URL in the exercise service.
# This is optional (omit or set to None). See the url option in the section
# "common for questionnaires and submittable exercises" below for more information.

default_configure_url = "{scheme}://{netloc}/configure"
# The default configuration URL.
# This is optional (omit or set to None). See the configure-url option in the section
# "common for questionnaires and submittable exercises" below for more information.

course_configures = []
# What files to send and where. This can be used to send additional course files
# to the grading services. E.g.
# course_configures = [
#     {
#         "url": "<grader domain>/configure",
#         "files": {
#             "fileongrader.txt": "file in repo.txt",
#         },
#     },
# ]
# sends the file "file in repo.txt" to the grader but renamed as "fileongrader.txt"

unprotected_paths = []
# List of static paths that should be accessible without login, e.g. downloadable files.
# _downloads, _static and _images are always added by Git Manager.
# The paths are relative to the static_dir in the output yaml. static_dir is generally
# the html output directory, i.e. _build/html.

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

# Default rules for revealing submission feedback and model solutions.
# Can be overridden in module aplusmeta directive, or in questionnaire/submit
# directives.
# See instructions in chapter 'Defining reveal rules'.
reveal_submission_feedback = 'immediate'
reveal_model_solutions = 'deadline'

# List of JavaScript and CSS URLs for the A+ head URLs course setting.
# A+ adds these to every course page. These can also be paths to static files,
# e.g. _static/course.js (only on gitmanager)
course_head_urls = [
    "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS_CHTML-full",
]

# a-plus-rst-tools try to detect the language of the chapter from the language
# suffix in the file name, e.g., chapter_en.rst. This detection can be disabled
# with this setting. If the course is multilingual, but the chapter files do not
# have language suffixes, it may be best to disable this. The detected language
# is used to translate strings that are part of a-plus-rst-tools and Sphinx.
# The language may also be detected from a language subdirectory (such as en)
# under the module directory, but using language subdirectories is not recommended.
# If the language can not be detected from the filename or the subdirectory,
# then the language set in conf.py is not modified.
enable_rst_file_language_detection = True

# Add the language suffix to doc and ref link targets as well as ref link
# labels in multilingual courses. This can only be used in multilingual courses
# that include the language suffix "_en" in each chapter RST file, that is,
# filenames are like chapter1_en.rst and chapter1_fi.rst.
# It is more convenient to write doc links without manually added language
# suffixes, e.g., :doc:`chapter1` instead of :doc:`chapter1_en`. This function
# adds the language suffixes automatically since Sphinx can not compile
# the link if the target file does not exist.
# Likewise, it is convenient to write identical ref link labels in the same
# place in all language versions of the chapter. Sphinx requires that labels
# are unique, thus language suffixes are automatically appended to the labels.
# The ref links in the RST chapters also refer to the labels without the
# language suffixes. The language suffixes are added automatically to
# the ref links.
# If the course uses a different format in links or for some other reason links
# need to stay untouched, set enable_doc_link_multilang_suffix_correction to
# False in order to disable doc link modifications and
# enable_ref_link_multilang_suffix_correction to False in order to disable
# ref link and label modifications.
enable_doc_link_multilang_suffix_correction = True
enable_ref_link_multilang_suffix_correction = True

# If True, autosave is enabled for all questionnaires in this course. A draft is
# saved periodically while a student types their answer, and the latest draft
# is automatically restored if the student leaves the exercise page and comes
# back later. A draft does not count as a submission and does not affect
# grading. Autosave can also be enabled for individual questionnaires.
enable_autosave = False
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
:unprotected_paths: "this/is/parsed" "into/a/list/of/paths" "like/a/shell/command"
```

Some fields require a value from specific choices (see also
[the MOOC-grader documentation about the index.yaml file](https://github.com/apluslms/mooc-grader/blob/master/courses/README.md)):

* `view-content-to`: enrolled, enrollment_audience, all_registered, public
* `enrollment-audience`: internal, external, all
* `index-mode`: results, toc, last, experimental
* `content-numbering` and `module-numbering`: none, arabic, roman, hidden


## List of directives and examples

### 1. Common options for questionnaires and submittable exercises

* `url`: the URL of the exercise in the assessment service. This is optional.
If omitted, it is set according to `default_exercise_url`. If that is omitted
as well, it is set by Git Manager to the value returned by the service at
`configure-url` (which should return the correct URL). Supports formatting
where `{key}` is replaced with the exercise key.
For example, "https://grader/{key}".
* `configure-url`: the URL that is used to configure the exercises on a
grader. It is dependent on the grading service used, and is `<domain>/configure`
for MOOC-grader. This is optional. If omitted, it is set according to
`default_configure_url`. If that is omitted as well, it is set by Git Manager
to the Git Manager instance's default value (MOOC-grader for Aalto).
Supports formatting with `{scheme}`, `{netloc}`, `{path}`, `{params}`,
`{query}` and `{fragment}` where the variables are parsed from the `url` option as
`<scheme>://<netloc>/<path>;<params>?<query>#<fragment>`.
For example, "{scheme}://{netloc}/configure".
* `configure-files`: Additional files to be sent to the grader as part of the exercise.
A comma separated list of mappings that define the file path on the grader and in the git repository.
The paths in a mapping are separated by a colon `:`.
If the file need not be renamed, the mapping may contain only the path in the repo.
For example, `extra/grader.txt:configs/repo.txt,files/not-renamed.txt`
sends the file `configs/repo.txt` from the git repo to the grader path `extra/grader.txt` and
the file `files/not-renamed.txt` is copied to the same path.
These additional files could be, for example, HTML template files.
* `no-override`: If set, the conf.py override setting is ignored.

### 2. Graded questionnaire

The questionnaire directive arguments define the exercise key and optional max points
with the difficulty. For example, `.. questionnaire:: 1 A50` sets key `1`,
max points `50` and difficulty `A`. If not set in the directive arguments, the max points will be set to
the sum of the question points. Setting the difficulty is optional and it can be set
even if the max points aren't defined in the argument. The questionnaire directive accepts the following options:

* `submissions`: max submissions (set to 0 to remove submission limit)
* `points-to-pass`: points to pass
* `feedback`: If set, assumes the defaults for a feedback questionnaire
* `title`: exercise title
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
  By default false. Don't use this option together with `reveal-model-solutions`.
* `show-model`: Students may open the model solution in A+ after the module
  deadline. Can be set to true or false. The default value can be set in
  index.rst with the field `questionnaire-default-show-model`. By default true.
* `allow-assistant-viewing`: Allows assistants to view the submissions of the students.
  Can be set to true or false. Overrides any options set in the conf.py or config.yaml files.
* `allow-assistant-grading`: Allows assistants to grade the submissions of the students.
  Can be set to true or false. Overrides any options set in the conf.py or config.yaml files.
* `reveal-submission-feedback`: rule for revealing submission feedback. See [instructions](#defining-reveal-rules).
* `reveal-model-solutions`: rule for revealing model solutions. See [instructions](#defining-reveal-rules).
* `grading-mode`: which submission determines the final score for this exercise ("best" or "last"). Defaults to "best".
  If delayed feedback is used (`reveal-submission-feedback` is set to something other than "immediate"), defaults to
  "last".
* `autosave`: If set, autosave is enabled for this exercise. A draft is saved periodically while a student types their
  answer, and the latest draft is automatically restored if the student leaves the exercise page and comes back later.
  A draft does not count as a submission and does not affect grading. Autosave can also be enabled for the entire
  course in conf.py.

The contents of the questionnaire directive define the questions and possible
instructions to students.

#### Question directives: multiple choice and text input

The **question directives** `pick-one`, `pick-any`, and `freetext` take the points
of the question as the first argument. If the questionnaire's max points are set, the sum
of the question points should be equal to them.
The question directives accept the following options:

* `class`: CSS class
* `required`: If set, the question is required and empty answers are rejected
* `key`: a manually set key for the question. This affects the HTML input element and
  the key in the submission data. If no key is set, note that automatically added
  keys change when the order and amount of questions is modified.

**The question directives may define instructions.** After the instructions,
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

**Multiple choice: pick-any and pick-one**

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
* `checkbox-feedback`: If set, the feedback for a selected checkbox is rendered
  under the checkbox instead of the list under the question. This makes it obvious
  to the student which checkbox triggered the feedback. Even if this is set,
  the inverse feedback (!a, when option is not selected) is still rendered under
  the question after all checkboxes. By default, all feedback is rendered under
  the question.

The `pick-one` questions are rendered with HTML radio buttons by default, but
a dropdown (select) element may be used with the `dropdown` option.

**Text input: freetext**

The `freetext` directive also accepts the following options in addition to
the common question options:

* `length`: (horizontal) length for the HTML text input
* `height`: If greater than 1, the textarea HTML element is used. Otherwise,
  a text input is used.
* Other options are defined in the code, but they mainly affect the CSS classes
  and they were implemented for very narrow usecases.

The `freetext` directive accepts a second positional argument after the points.
It defines the compare method for the model solution.
A textual input can be compared with the model solution as

* `int`,
* `float`,
* `string`,
* `subdiff`,
* `regexp` or
* `unsortedchars` (unsorted character set).

The `regexp` compare method takes the correct answer as a regular
expression and tries to match the submission with it.
It is possible to provide a separate display model solution
that is shown to the students in the model solution.
Otherwise, the students would be shown the whole regular expression.
The display model solution is added after the model regular expression
with the special characters `°=°`.
For example,

```
/cat|dog/ °=° dog
```

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

The body of the `freetext` question is
expected to be its model solution. However, the question instructions can be written
inside the body before the model answer. The instructions and the model solution must
be separated with an empty line.

If the questionnaire has the `feedback` option set, `freetext`
questions may not have a model solution and the body of the question is shown as the
question instructions.

#### Questionnaire example in RST markup

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
    The submission is graded by a regular expression.
    When the student is shown the model solution, it shows `red`.

    red|blue °=° red
```

### 3. Feedback questionnaire

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

Note that the [mooc-jutut service](https://github.com/apluslms/mooc-jutut/)
provides a more advanced method for reading and responding to feedback.
In order to use it, you still define the feedback questionnaire in RST, but
you must also set the service URL of the questionnaire exercise to the mooc-jutut
server. The URL can be set by using the override option in the project conf.py
file. For example:

```python
override = {
    'feedback': {
        'url': 'https://jutut-server.org/feedback/coursekey/{key}',
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

### 4. Submittable exercise

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
* `submissions`: max submissions (set to 0 to remove submission limit)
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
* `reveal-submission-feedback`: rule for revealing submission feedback. See [instructions](#defining-reveal-rules).
* `reveal-model-solutions`: rule for revealing model solutions. See [instructions](#defining-reveal-rules).
* `grading-mode`: which submission determines the final score for this exercise ("best" or "last"). Defaults to "best".
  If delayed feedback is used (`reveal-submission-feedback` is set to something other than "immediate"), defaults to
  "last".
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

### 5. External exercise (LTI)

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

### 6. Meta (exercise round settings)

The aplusmeta directive is used to define module (exercise round) settings.
It should be defined in the RST file that defines the `toctree` of the module
(module index). Furthermore, it may be used in chapters to hide them (i.e., set status hidden)
with the `hidden` option or to set the chapter audience with the `audience` option.

The aplusmeta directive does not have any content and it accepts the following options:

* `open-time`: module open time, e.g., 2019-01-31 23:59:00 (the time defaults to 12:00 if excluded)
* `close-time`: module close time
* `late-time`: module late submission time
* `late-penalty`: module late penalty between 0-1, e.g., 0.5 (50%)
* `read-open-time`: module read open time. The reading materials can be opened for reading before the exercises are opened for submissions.
  The exercise descriptions are hidden and submissions are disabled between the read open time and open time.
* `audience`: chapter audience (internal, external, or registered. Defaults to the course audience)
* `hidden`: If set, set status hidden for the module or chapter
* `points-to-pass`: module points to pass
* `introduction`: module introduction as an HTML string
* `reveal-submission-feedback`: default rule for revealing submission feedback. Can be overridden per exercise. See [instructions](#defining-reveal-rules).
* `reveal-model-solutions`: default rule for revealing model solutions. Can be overridden per exercise. See [instructions](#defining-reveal-rules).

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


### 7. Active element input

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


### 8. Active element output

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

### 9. Hidden block

Directive for creating hidden content blocks. The content can be shown/hidden
by clicking the link. (This uses the Bootstrap collapse component.)

```
.. hidden-block:: name (required)
  :label: Optional text for the show/hide link (default Show/Hide)
  :visible: # if this flag is present, the collapsible div starts out visible

  Hidden content here.
```

### 10. Point of interest

Directive for creating a "point of interest" summary block.
This extension must be activated separately in the project conf.py
(`extensions = ["aplus_setup", "point_of_interest"]`).
A point of interest is mostly like a normal admonition ("coloured info box"), but
they are also linked to each other with next/previous links. The links enable
the user to quickly navigate between the points of interest.

Point of interests may also be used to generate separate lecture slides
(not directly included in the A+ content chapters). This requires a separate
tool called [Presentation maker](https://github.com/apluslms/presentation-maker).

More information about [Columns and rows](#18-columns-and-rows).
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


### 11. Annotated code blocks

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

### 12. Code blocks with line references

With the `lineref-code-block`, you may add links from the chapter contents to
specific lines of the code block. You define labels enclosed in `::` for lines
of the code block. Labels can include alphanumeric characters, underscore (_),
and hyphen (-). The directive is used similarly to the Sphinx directive `code-block`.
This extension must be activated separately in the project conf.py
(`extensions = ["aplus_setup", "codeblock_lineref"]`).

This directive has limitations (that have not been fixed thus far):

* The `lref` link can only refer to code blocks in the same RST file.
* The code block containing the label must be defined before the `lref` link that refers to the label.
  Otherwise, the link does not work.
  In other words, you can not link to the code block in the chapter text before the code block.

```
.. lineref-code-block:: python
  :linenos:

  def example():
      :my-label-name:var = "something"
      return var

The role lref makes it possible to link to labels defined in lineref-code-block blocks:
:lref:`optional link text <my-label-name>`.
```

### 13. REPL sessions

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

### 14. Submittable ACOS exercises

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

### 15. HTML div elements

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

### 16. CSS styled topics

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

### 17. Media directives

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

### 18. Columns and rows

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

### 19. Tabs

The `rst-tabs` directive is designed to add tabbed content. Tabs separate content into different panels so that one
panel is displayed at a time. This extension must be activated separately in the project by adding the following
settings to the **conf.py** file located in the root of your course directory.

```python
extensions = ["aplus_setup", "tabs"]
...
include_tab_js = True
include_tab_css = True
```

This directive requires a custom JavaScript and CSS implementation for interacting with the tabs and the tab content.
Therefore, we have added a default implementation that allow you to make use of the `rst-tabs` directive without having
to write your own JS or CSS. However, if you want to remove the default JavaScript and CSS implementation, you can
change the value of `include_tab_js` and `include_tab_css` to `False`. By doing so, you could write your own CSS and JS
code to interact with the `rst-tabs` directive.

The following snippet of code is an example on how you can use the `tabs` extension. As you can see in the example
below.

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

The `rst-tabs` directive should contain one or more `tab-content` directives. Each `tab-content` requires one argument,
which is used internally to identify individual `tab-content`. Therefore, this argument must be unique and cannot
contain any whitespace. You must also add the option `title` to the `tab-content` directive since it is the title that
will be shown in your tabs. The content of each `tab-content` can be any anything.

### 20. Interactive code
The `thebe-button` or `thebe-precell-button` directives and `thebe` class can be used to make python, R and
C/C++ code-blocks interactive, allowing students to edit and run code.
This extension must be activated separately in the project by adding `"thebe"` to the `extensions` list variable in the **conf.py** file located in the root of your course directory.

```python
extensions = ["aplus_setup", "thebe"]
```

Additionally, **conf.py** should contain the following configuration to use
interactive code blocks.

```python

   # Thebe configuration
    thebe_config = {
      "binderUrl": "https://mybinder.org" # For testing; replace this with a binderhub server provided by your instution for production
      # "repository_url": "",
      # "repostiory_branch": "",
      "selector": "div.highlight",
      "codemirror-config": {
          "theme": "eclipse",
          "electricChars": "true"
          "lineNumbers": "true",
          "indentWithTabs": "true",
          "indentUnit": 4,
      }
    }
```
The kernel configuration fields, which configure a production binderhub server that
can run the environment residing in a remote repository, are followed by
`"selector"` configuration. The last configuration ultimately defines which `rst`
code blocks should be converted to interactive code elements. If this configuration is
- `"selector": "div.highlight"` all the code blocks in `rst` files starting or
containing `:thebe-kernel: <KERNEL-NAME-HERE>` directive will be converted to
interactive code blocks.
- `"selector": ".thebe"` the code blocks containing `:class: thebe` option will be
converted to interactive code blocks. This is the default option, and if it is
desired to have all code blocks to be interactive code blocks,
`"selector": "div.highlight"` should be explicitly configured.

You can also configure the editable code area behavior in `thebe_config`
as follows.
1. `"theme": "eclipse"` configuration option states the editor code style theme.
We support only two options for now
   - `"theme": "eclipse"` (default). This theme is very similar to the default theme
   of Eclipse IDE, and has a light background, which makes it a natural choice
   for the default A+ style in general.
   - `"theme": "abcdef"`. This is a colorful theme with a dark background.
2. `"electricChars": "true"` configuration option sets whether the editor
(interactive code block) should re-indent the current line when a character is typed.
Change this configuration to `"false"` if you prefer the students to practice proper
indentation. Default is `"true"`.
3. `"lineNumbers": "true"` configuration enables line numbering. When enabled, the
editor will have a left gutter area with line numbers. The default is `"true"`,
and should be explicitly set to `"false"` if you do not want to have line numbers.
4. `"indentWithTabs": "true"` configuration enables indentation with tabs. The
default configuration is `"true"`, and should be set to `"false"` if you prefer
to use spaces for indentation. A tab has `4` characters width.
5. `"indentUnit": 4` configuration sets how many spaces define an indented block.
The default is `4` spaces, and should be explicitly configured to change the indentation experience.

- In addition to these, the matching braces are highlighted when one of
(`}`, `)` or `]`) is typed.

The following code snippets are examples on how you can use the `thebe` extension. The `thebe-button` directive makes an activation button that looks good on its own, and the `thebe-precell-button` makes an activation button that looks nice when placed just before a code cell.

```rst
:thebe-kernel: python

.. thebe-button:: Custom button text (defaults to "Run code")

.. code-block:: python
  :class: thebe

  a = 1
  b = 2
  c = a + b
  print(c)
```

```rst
:thebe-kernel: python

.. thebe-precell-button:: Custom button text (defaults to "Activate")
.. code-block:: python
  :class: thebe

  a = 1
  b = 2
  c = a + b
  print(c)
```

### List of exercise statuses

There are 6 possible statuses for exercises:

* ready: Visible exercise listed in table of contents.
* unlisted (default): Unlisted in table of contents, otherwise same as ready.
* hidden: Hidden from non course staff.
* enrollment: Questions for students when they enroll to a course.
* enrollment_ext: Same as enrollment but for external students.
* maintenance: Hides the exercise description and prevents submissions.

### Defining reveal rules

Rules for revealing submission feedback (`reveal-submission-feedback`) and model solutions (`reveal-model-solutions`)
can be defined and overridden on multiple levels:

* course level, in conf.py
* module level, in the `aplusmeta` directive
* exercise level, in the `questionnaire`/`submit` directive

The reveal rules are defined by providing the name of a reveal mode. Some of the modes also accept arguments after the
mode name. The reveal modes are:

* manual: Never revealed, unless a teacher manually reveals it in A+ exercise settings.
* immediate: Always revealed. **This is the default setting for revealing submission feedback.**
* time: Revealed at a specific time. The reveal date and time must be provided as an argument, in the format
`YYYY-MM-DD [hh[:mm[:ss]]]` or `DD.MM.YYYY [hh[:mm[:ss]]]`. Examples:
```
:reveal_submission_feedback: time 2020-01-16
:reveal_submission_feedback: time 2020-01-16 16
:reveal_submission_feedback: time 16.01.2020 16:00
:reveal_submission_feedback: time 16.01.2020 16:00:00
```
* deadline: Revealed after the exercise deadline, and the possible deadline extension granted to the student. **This is
the default setting for revealing model solutions.** An additional delay can optionally be provided as an argument, in
the format `+<number><unit>`, where `unit` is 'd' (days), 'h' (hours) or 'm'/'min' (minutes). Examples:
```
:reveal_submission_feedback: deadline
:reveal_submission_feedback: deadline +1d
:reveal_submission_feedback: deadline +2h
:reveal_submission_feedback: deadline +30m
:reveal_submission_feedback: deadline +30min
```
* deadline_all: Revealed after the exercise deadline, and all deadline extensions granted to any student on the course.
An additional delay can optionally be provided as an argument. See instructions above.
* completion: Revealed after the student has used all submissions or achieved full points from the exercise.
