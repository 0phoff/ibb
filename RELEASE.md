1. __Release a new version of ibb on PyPI:__  
Update \_version.py (set release version, remove 'dev')  
git add the \_version.py file and git commit  

```bash
pip install twine
python setup.py sdist bdist_wheel

# Test server
twine upload -r testpypi dist/*

# Real server
twine upload dist/*
git tag -a X.X.X -m 'comment'
```

---

2. __Release a new version of ibb on NPM:__  
Update `js/package.json` with new npm package version

```bash
# clean out the `dist` and `node_modules` directories
git clean -fdx

npm install
npm publish
```

---

3. __Setup version for next dev cycly:__  
Update \_version.py (add 'dev' and increment minor)  
git add and git commit

```bash
git push
git push --tags
```
