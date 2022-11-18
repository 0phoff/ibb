# RELEASE NOTES
Quick notes about releasing a new version of this package.
For more information, visit the [cookiecutter page](https://github.com/jupyter-widgets/widget-ts-cookiecutter).


## Releasing your initial packages:

1. `git checkout develop`
1. Make sure all changes are pushed to remote and CI is OK.
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
1. Change versions in `_version.py`, `package.json` and `pyproject.toml`.
   Make sure you input exactly the same numbers !
1. Commit version changes on both `develop` and `master`:
   ```
   git add -u
   git commit -m 'Bumped version to X.Y.Z'
   git checkout master
   git merge --ff-only develop
   git checkout develop
   ```
1. `yarn build` (do not forget to activate the correct python environment)
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
1. Update the version in `_version.py`, `package.json` and `pyproject.toml` (back to 'dev' versions).
1. Commit the changes in `develop`.
1. Push online `git push --all && git push --tags`.
1. Verify [PyPi](https://pypi.org/project/ibb), [NPM](https://www.npmjs.com/package/ibb) and [readthedocs](https://ibb.readthedocs.io).
   Note that some may take a while to show the changes.
