A-plus RST tools
================

Provides tools to publish RST course content for mooc-grader and a-plus.

* http://www.sphinx-doc.org/en/stable/
* http://matplotlib.org/sampledoc/
* http://docutils.sourceforge.net/rst.html


Creating a new course
---------------------

We recommend to start with a fork from the mooc-grader-rst-course repository
from Github.

    git clone -b rst --recursive https://github.com/Aalto-LeTech/mooc-grader-course.git

To compile the RST source into HTML the Python sphinx module is required.

    pip install sphinx

The course is compiled with a make.

    make

The tools can be later upgraded.

    git submodule update


Adding tools to existing course
-------------------------------

The tools can be added into a repository as a submodule.

    git submodule add git@github.com:Aalto-LeTech/a-plus-rst-tools.git a-plus-rst-tools

Then installation of sphinx, creation of RST document root and configuring sphinx are required.

    pip install sphinx
    sphinx-quickstart
    cp a-plus-rst-tools/conf.py .



List of directives and examples
-------------------------------

1. Graded questionnaire

```
    .. questionnaire:: 1 A50
      :submissions: 4
      :points-to-pass: 0

      This is a questionnaire number 1 that gives at maximum 50 points
      in category A. Students can make at most 4 submissions.
      This exercise is marked passed when 0 points is reached (the default).

      .. pick-one:: 10

        What is 1+1?

        a. 1
        *b. 2
        c. 3

        !b § Count again!
        c § Too much

      (Hints can be included or omitted in any question.)

      .. pick-any:: 10

        Pick two **first**.

        *a. this is **first**
        *b. this is **second**
        c. this is **third**

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

This creates an input field for active element

    .. ae-input:: id-for-input
    	:title: title of the input (displayed on the html page)
    	:default: default value for the input (displayed when the user has not submitted a solution)
    	:class: In the example css-file classes "active-element" and "ae-input" 
             are used to style the input element and can be modified as needed.
             The classes left and right can be used to float the box left or right,
             or center to align it centered. 
    	:width: can be used to determine the width of the element 
    	:height: can be used to determine the height of the input textarea (deafult with classes "active element" and "ae-input" is 150px)
    	:clear: 'both' forces the element to a new line, 'left' ('right') allows no floating elements on the left (right)
    	:type: use "file" for file inputs and "dropdown" for dropdown. For dropdowns, the available options
            should be listed after the type indicating "dropdown" in this format: "dropdown:option1,option2,option3"
            
            
5. Active element output

This creates an input field for active element

    .. ae-output:: key-for-output
    	:config (required): path to the exercise configuration file
    	:inputs (required): ids of the input elements required for the output
    	:title: title of the output element
    	:class: In the example css-file the classe "active-element" is used to style the input element 
             and can be modified as needed.
             The classes left and right can be used to float the box left or right,
             or center to align it centered. 
             Class "no-border" can be used to remove the output box border.
    	:width: can be used to determine the width of the element
    	:height: can be used to determine the height of the output div (deafult with class "active element" is 150px) 
    	:clear: 'both' forces the element to a new line, 'left' ('right') allows no floating elements on the left (right)
    	:type: default type is text; for image (png) outputs use "image"
    	:submissions: number of allowed submissions (default is unlimited for active elements)
    	:scale-size: no value; if this option is present, the output element height will scale to match content that has a defined height

