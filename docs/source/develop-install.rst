
Developer install
=================


To install a developer version of ibb, you will first need to clone the repository::

    git clone https://github.com/0phoff/ibb
    cd ibb

Next, install it in a new environment with a develop install using conda::

    conda create -n ibb-dev -c conda-forge nodejs yarn jupyterlab python=3.10
    conda activate ibb-dev
    pip install -e .[examples,docs]


If you are planning on working on the JS/frontend code, you should also do a link installation of the extension (with the `appropriate flag`_)::

    jupyter nbextension install --sys-prefix --symlink --py ibb
    jupyter nbextension enable --sys-prefix --py ibb

Or, if you are using Jupyterlab::

    jupyter labextension develop --overwrite .

Finally, build the extension and test the examples::

    yarn run build

    # Option 1: Jupyter Notebook
    jupyter notebook

    # Option 2: JupyterLab
    jupyter lab


.. note::
   In order for the documentation to contain the widgets, you need to run the notebook in a `Jupyter Notebook` environment.
   Run the entire notebook, set the widgets to a good view and click on `Widgets > Save widget states`.


.. links
.. _`appropriate flag`: https://jupyter-notebook.readthedocs.io/en/stable/extending/frontend_extensions.html#installing-and-enabling-extensions
