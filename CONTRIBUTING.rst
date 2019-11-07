Contributing to gd.py
=====================

First of all, we are glad that you decided to contribute to our project.

Guidelines
----------

Here are some simple guidelines for creating good issues and pull requests:

    1. When deciding to contribute, please check if there is already a solution for the problem;

    2. We appreciate any contribution, whether it is a typo fix or huge addition to the project;

    3. When creating any code changes, remember that code style really matters;

        3.1. We are trying to follow PEP 8 within our code;

        3.2. Though, our line length limit is 120 characters, and we tend to use more space to bring the readability;

    4. If you have created a new function or method, please document it; that really helps end-users of our library;

    5. Lastly, see some examples below related to the code style.

Code Style
----------

.. code-block:: python3

    # bad
    from some_module import *  # really makes reading code confusing

    var=my_function()  # use more spaces, as PEP 8 suggests

    if condition: do_something()  # never do one-line if statements

    # good
    from some_module import (
        my_function, condition, do_something
    )

    var = my_function()

    if condition:
        do_something()

Additional Commentary
---------------------

Questions regarding the library should be asked in the official server,
however, if you are sure it should belong to GitHub, feel free to open a new issue.
