# scope-web

## Using Pipenv

This project uses [Pipenv](https://pipenv.pypa.io/en/latest/) to manage a virtual environment and to pin dependencies.

Ensure Pipenv is globally installed. From your preferred Python installation:

```
pip install pipenv
```

Create a virtual environment and install dependencies, including development dependencies:

```
pipenv install --dev
```

Launch a shell inside the environment:

```
pipenv shell
```

  - The shell has some limitations on Windows (e.g., lacks arrow key access to command history). You can instead:

    ```
    pipenv run cmd
    ```

Install a new dependency, including updating `Pipefile` and `Pipefile.lock`:

```
pipenv install <package>
```

## Using Invoke

This project uses [Invoke](https://www.pyinvoke.org/) for task execution.

List available tasks:

```
invoke -l
```

## Old README Content

This app uses

- react
- typescript
- webpack

## Website
### Pre-requisites

- node https://nodejs.org/en/download/ (tested with npm 6.14.10 and node 14.15.4)
- yarn https://yarnpkg.com/ (`npm install -g yarn` for first install, `yarn set version latest` to upgrade, tested with yarn 1.22.10)
- code https://code.visualstudio.com/
- prettier https://github.com/prettier/prettier-vscode

### To run the site

```
yarn
npm start
```

## Web server
### Pre-requisites

- python 3.5 and newer
- Flask https://flask.palletsprojects.com/en/1.1.x/installation/
- Create a python virtual environment using your favorite python virtual environment tool (pyenv, venv, conda)

### To run the server

[Be sure to activate your python virtual environment]
```
pip install -r requirements.txt
npm run server
```
