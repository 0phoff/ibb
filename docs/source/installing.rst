
.. _installation:

Installation
============


The simplest way to install ibb is via pip::

    pip install ibb

or via conda::

    conda install ibb


If you installed via pip and notebook version < 5.3, you will also have to install / configure the front-end extension as well.
If you are using classic notebook (as opposed to Jupyterlab), run the following commands (with the `appropriate flag`_)::

    jupyter nbextension install [--sys-prefix / --user / --system] --py ibb
    jupyter nbextension enable [--sys-prefix / --user / --system] --py ibb

If you are using Jupyterlab, install the extension with::

    jupyter labextension install ibb

.. note::

  If you are installing using conda, these commands should be unnecessary.
  If you still need to run them, the commands should be the same (just make sure you choose the `--sys-prefix` flag).


.. links
.. _`appropriate flag`: https://jupyter-notebook.readthedocs.io/en/stable/extending/frontend_extensions.html#installing-and-enabling-extensions
