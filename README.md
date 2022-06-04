# MDA-project

## Water security
### Team Poland

The following command creates an environment called `mda_project`, and downloads all dependencies from the `environment.yml` file.
```
conda env create -n mda_project -f environment.yml
```

#### Heroku usage
Between step 5 and step 6 in the slides of prof. de Spiegeleer, the following command is required to connect the remote repository to your local machine
```
heroku git:remote -a mda-poland
```
Then, instead of pushing to heroku `master`, push to `main`. Note that if you push from a branch (e.g. `app`) towards heroku, then do 
```
git push heroku app:main
```