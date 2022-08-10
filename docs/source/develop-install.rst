
Developer install
=================


To install a developer version of ibb, you will first need to clone the repository::

    git clone https://github.com/0phoff/ibb
    cd ibb

Next, install it with a develop install using pip::

    pip install -e .


If you are planning on working on the JS/frontend code, you should also do a link installation of the extension (with the `appropriate flag`_)::

    jupyter nbextension install [--sys-prefix / --user / --system] --symlink --py ibb
    jupyter nbextension enable [--sys-prefix / --user / --system] --py ibb

Or, if you are using Jupyterlab::

    jupyter labextension install .


.. links
.. _`appropriate flag`: https://jupyter-notebook.readthedocs.io/en/stable/extending/frontend_extensions.html#installing-and-enabling-extensions
