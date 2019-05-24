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

    git submodule add https://github.com/Aalto-LeTech/a-plus-rst-tools.git a-plus-rst-tools
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


## List of directives and examples

### 1. Graded questionnaire

The questionnaire directive arguments define the exercise key and max points
with the optional difficulty. For example, `.. questionnaire:: 1 A50` sets key `1`,
max points `50` and difficulty `A`.
The questionnaire directive accepts the following options:

* `submissions`: max submissions
* `points-to-pass`: points to pass
* `feedback`: If set, assumes the defaults for a feedback questionnaire
* `no-override`: If set, the conf.py override setting is ignored
* `pick_randomly`: integer. Set the pick_randomly setting for the quiz
  (select N questions randomly on each load)
* `category`: exercise category

The contents of the questionnaire directive define the questions and possible
instructions to students.

The **question directives** `pick-one`, `pick-any`, and `freetext` take the points
of the question as the first argument. The sum of the question points should
be equal to the questionnaire max points.
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
A textual input can be compared with the model solution as `int`, `float`, `string`,
or `unsortedchars` (unsorted character set).
Another option is `regexp` that takes the correct answer as a regular
expression and tries to match the submission with it.
Strings have comparison modifiers that are separated with a hyphen.
For example, `.. freetext:: 30 string-ignorews-ignorequotes`.

* `ignorews`: ignore white space (applies to regexp too)
* `ignorequotes`: iqnore "quotes" around
* `requirecase`: require identical lower and upper cases (only with the string type)
* `ignorerepl`: ignore REPL prefixes
* `ignoreparenthesis`: ignore parenthesis "( )"

The question directives may define instructions. After the instructions,
the contents of the directive define the choices, the correct solution, and
possible hints. The hints are targeted to specific choices and they are shown
after answering. See the example below.

```
.. questionnaire:: 1 A60
  :submissions: 4
  :points-to-pass: 0

  This is a questionnaire number 1 that grants at maximum 50 points
  of difficulty A. Students can make at most 4 submissions.
  This exercise is marked passed when 0 points are reached (the default).

  .. pick-one:: 10
    :required:

    What is 1+1?

    a. 1
    *b. 2
    c. 3

    !b § Count again!
    c § Too much

  (Hints can be included or omitted in any question.)

  .. pick-any:: 10

    Pick the two **first**.

    *a. this is the **first**
    *b. this is the **second**
    c. this is the **third**

  .. freetext:: 30 string-ignorews-ignorequotes
    :length: 10

    A textual input can be compared with the model solution as integer, float or string.
    Here the correct answer is "test". Surrounding quotes are ignored in the solution
    as well as whitespace everywhere (modifiers ignorequotes and ignorews).

    test
    !test § Follow the instruction.

  .. freetext:: 10 regexp

    This question accepts either "red" or "blue" as the correct answer.
    The model solution is a regular expression.

    red|blue
```

### 2. Feedback questionnaire

A feedback questionnaire is basically just like a graded questionnaire, but with
the `feedback` option it uses the feedback category and CSS class by default.
The options `chapter-feedback`, `weekly-feedback`, `appendix-feedback`, and
`course-feedback` use a different CSS class (with the same name as the option).
If points are not specified, they are set to zero.

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
It accepts the following options:

* `config`: path to the YAML configuration file
* `submissions`: max submissions
* `points-to-pass`: points to pass (default zero)
* `class`: CSS class(es)
* `title`: exercise title
* `category`: exercise category (default "submit")
* `ajax`: If set, the A+ chapter does not attach any JavaScript event listeners
  to the exercise and the exercise JS may control the submission itself.
  See [the chapter content documentation](https://github.com/Aalto-LeTech/a-plus/blob/master/doc/CONTENT.md)
  (the HTML attribute `data-aplus-ajax`).
* `quiz`: If set, the exercise feedback will take the place of the exercise instructions.
  This makes sense for questionnaires since their feedback contains the submission form.
  In RST, you would usually define questionnaires with the questionnaire directive,
  but they can also be defined in a YAML file.
  See [the chapter content documentation](https://github.com/Aalto-LeTech/a-plus/blob/master/doc/CONTENT.md)
  (the HTML attribute `data-aplus-quiz`).
* `url`: the service URL of the exercise. Use this if the URL must, for example,
  refer to another server.
* `radar_tokenizer`: [See the Radar similarity analysis tool][Radar service]
* `radar_minimum_match_tokens`: [See the Radar similarity analysis tool][Radar service]
* `lti`: See LTI exercises in the next section. This option defines the label of
  the LTI service that must be configured in the A+ site beforehand.
* `lti_resource_link_id`: LTI exercise key
* `lti_context_id`: LTI course key

[Radar service]: https://github.com/Aalto-LeTech/radar

```
.. submit:: 2 A100
  :submissions: 100
  :config: exercises/hello_python/config.yaml
```

### 4. External exercise (LTI)

This exercise opens an external tool via the LTI launch protocol.
The LTI service must be configured beforehand in A+ by an administrator.
The `lti` option refers to the label of the LTI service.
The `url` option may exclude the domain of the service URL since the domain
must be equal to the URL defined in the LTI service anyway.
The LTI parameters may be defined in the config.yaml file linked with
the `config` option, thus it is not required to define them in RST.

```
.. submit:: 3 B50
  :lti: Rubyric
  :url: /aplus/123
  :lti_resource_link_id: example1
```

### 5. Meta (exercise round settings)

The meta directive is used to define module (exercise round) settings.
It should be defined in the RST file that defines the `toctree` of the module
(module index). Furthermore, it may be used in chapters to hide them (i.e., set status hidden)
with the `hidden` option or to set the chapter audience with the `audience` option.

The meta directive does not have any content and it accepts the following options:

* `open-time`: module open time, e.g., 2019-01-31 23:59:00 (the time defaults to 12:00 if excluded)
* `close-time`: module close time
* `late-time`: module late submission time
* `late-penalty`: module late penalty between 0-1, e.g., 0.5 (50%)
* `audience`: chapter audience (internal, external, or registered. Defaults to the course audience)
* `hidden`: If set, set status hidden for the module or chapter
* `points-to-pass`: module points to pass
* `introduction`: module introduction as an HTML string


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

```
.. point-of-interest:: Title text
  :id: unique id, if not supplied a random id will be generated
  :previous: id of previous point-of-interest (optional)
  :next: id of next point-of-interest (optional)
  :hidden: (if this flag is present, the content of this poi is hidden by default)
  :class: any additional css classes
  :height: fixed height in pixels
  :columns: relative width of each column (e.g. for three columns 2 2 3)
  :bgimg: path to background image

  Content of point-of-interest here.

  Use ::newcol to start a new column:

  ::newcol

  New column starts here. If :columns: option not present columns of equal width will be created.
```


### 10. Annotated code blocks

Code blocks may be annotated with comments for specific lines. This extension
must be activated separately in the project conf.py
(`extensions = ["aplus_setup", "annotated"]`).
This extension requires custom JavaScript code and CSS styles in order to
highlight the annotations on mouse hover in the web browser. The frontend code
is not distributed in this repository (or anywhere).

```
.. annotated::

  .. code-block:: python

    1«x = "hello"»
    2«print(x + " world")»
    print("Last line without any annotation")

  .. annotation::

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

### 13. Media directives

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

