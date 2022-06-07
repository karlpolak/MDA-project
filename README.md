# MDA-project

## Water security
### Team Poland

The following command creates an environment called `mda_project`, and downloads all dependencies from the `environment.yml` file.
```
conda env create -n mda_project -f environment.yml
```

#### Requirements.txt
```
pyenv virtualenv 3.10.4 MDA-project
pyenv activate MDA-project
pip install -r requirements.txt
```
**Note:** if in `3. Classification.ipynb` you encounter problems importing the imbalanced-learn (imblearn) package, please do the following install (pip or conda) manually:

```
pip install -U imbalanced-learn
```
or
```
conda install -c conda-forge imbalanced-learn
```
