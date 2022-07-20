# RELEASE NOTES
Quick notes about releasing a new version of this package.  
For more information, visit the [cookiecutter page](https://github.com/jupyter-widgets/widget-ts-cookiecutter).


## Releasing your initial packages:

1. Make sure examples work in Jupyter Lab.
1. Make sure examples work in Jupyter Notebook.  
   For each notebook, follow this procedure:
     - Widgets > Clear widget states
     - Run notebook entirely
     - Setup widgets on a nice view
     - Widgets > Save widget states
     - Save and Close notebook
1. Create documentation and check everything looks fine locally.
1. Check linting for JS code: `yarn run lint`.
1. Change versions in `_version.py` and `package.json`.  
   Make sure you input exactly the same numbers !
1. Create a release commit.
1. Relase the npm packages:
   ```bash
   npm login    # Optional, if not already done
   npm publish
   ```
1. Release python packages:
   ```bash
   pip install build twine   # Optional, if not already done
   rm -rf dist/*
   
   python -m build .
   twine check dist/*
   twine upload dist/*
   ```
1. Tag the release commit: `git tag vX.Y.Z`.
1. Update the version in `_version.py` and `package.json` (back to 'dev' versions).
1. Commit the changes.
1. Push online `git push && git push --tags`.
1. Verify [PyPi](https://pypi.org/project/ibb), [NPM](https://www.npmjs.com/package/ibb) and [readthedocs](https://ibb.readthedocs.io).  
   Note that some may take a while to show the changes.