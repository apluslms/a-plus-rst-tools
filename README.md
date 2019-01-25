A-plus RST tools
================

Provides tools to publish RST course content for mooc-grader and a-plus.

* http://www.sphinx-doc.org/en/stable/
* http://matplotlib.org/sampledoc/
* http://docutils.sourceforge.net/rst.html


Creating a new course
---------------------

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


Adding tools to an existing course
----------------------------------

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


Upgrading the tools
-------------------

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


Special Sphinx configurations (conf.py)
---------------------------------------

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
override = {} # Hack for modifying exercise configurations based on category.
# The override dict uses category names as keys and the exercise configurations
# are updated at the end with the dict corresponding to the category.
# The category used is usually the hardcoded default (such as 'submit') instead
# of the manually set category.
# Using the hacks is not recommended!

category_names = {} # dict from category keys to category names
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

**Sphinx configurations that should be modified with a-plus-rst-tools**

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


List of directives and examples
-------------------------------

1. Graded questionnaire

  The questionnaire directive arguments define the exercise key and max points
  with the optional difficulty.
  In addition to the options shown in the example below, you may use the following
  options in the questionnaire directive:
  
  * `feedback`: If set, assumes the defaults for a feedback questionnaire
  * `no-override`: If set, the conf.py override setting is ignored
  * `pick_randomly`: integer. Set the pick_randomly setting for the quiz (select N questions randomly on each load)
  * `category`: exercise category

```
.. questionnaire:: 1 A50
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

    A textual input can be compared with the model as int, float or string.
    Fourth option is regexp which takes the correct answer as a regular
    expression. Strings have comparison modifiers that are separated with hyphen.

    * ignorews: ignore white space (applies to regexp too)
    * ignorequotes: iqnore "quotes" around
    * requirecase: require identical lower and upper cases
    * ignorerepl: ignore REPL prefixes

    Here the correct answer is "test".

    test
    !test § Follow the instruction.
```

2. Feedback questionnaire

```
    .. questionnaire::
      :feedback:

      What do you think now?

      .. freetext::
        :required:
        :length: 100
        :height: 4
        :class: my-input-class

      .. agree-group::

        .. agree-item:: Did it work for you?
```

3. Submit an exercise

These type of exercises are configured separately for mooc-grader.
The directive will attach the exercise at this position.

```
    .. submit:: 2 A100
      :submissions: 100
      :config: exercises/hello_python/config.yaml
```

4. Submit a remote exercise

This exercise opens an external tool via LTI launch protocol.

    .. submit:: 3 B50
      :url: https://rubyric.com/edge/exercises/111/lti
      :lti: Rubyric+
      :lti_context_id: asdasd
      :lti_resource_link_id: asdasd


5. Active element input

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
    	       (deafult with classes "active element" and "ae-input" is 150px)
    	:clear: "both" forces the element to a new line, "left" ("right") allows
    	       no floating elements on the left (right)
    	:type: use "file" for file inputs, "clickable" for clickable inputs, and
            "dropdown" for dropdown. For dropdowns, the available options should
            be listed after the type indicating "dropdown" in this
            format: "dropdown:option1,option2,option3"
      :file: (only for type clickable) path to the html file that contains
            the default clickable input


5. Active element output

This creates an output field for active element

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
    	:height: can be used to set the height of the output div (deafult
    	       with class "active element" is 150px)
    	:clear: "both" forces the element to a new line, "left" ("right") allows
    	       no floating elements on the left (right)
    	:type: default type is text; for image (png) outputs use "image"
    	:submissions: number of allowed submissions (default is unlimited for
    	       active elements)
    	:scale-size: no value; if this option is present, the output element
    	       height will scale to match content that has a defined height

6. Hidden block

Directive for creating hidden content blocks.

```
  .. hidden-block:: name (required)
    :label: Optional text for the show/hide link (default Show/Hide)
    :visible: # if this flag is present, the collapsible div starts out visible

    hidden content here
```

7. Point of interest

Directive for creating "point of interest" summary block.

```
.. point-of-interest:: name (unique id within the document)
    :title: optional title text
    :previous: name of previous point-of-interest (optional)
    :next: name of next point-of-interest (optional)
    :hidden: (if this flag is present, the content of this poi is hidden by default)
    :class: any additional css classes

    Content of point-of-interest here
```
