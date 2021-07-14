# scope-web

Core Scope components, including:

- Web client for provider registry in `src`
- Application Server in `server/flask`

## Typical Development Environment

With prerequisites:

- Dependencies installed (as in [Installation of Dependences](#installation-of-dependencies)).
- Secrets provided (as in [Providing Secrets](#providing-secrets))

A typical development environment then:

- Opens a tunnel to the production database 
  (i.e., because we cannot run the database locally, because production is currently our only instance).
- Runs a Flask application server development instance locally, with hot reloading.  
- Runs a web client development instance locally, with hot reloading.  

Within a Pipenv shell (as in [Using Pipenv](#using-pipenv)):

```
invoke dependencies.ensure.dev  # Ensure dependencies are installed, including development dependencies.
invoke database.forward.prod    # Forward the database from our production server, listening on `localhost:8000`.
invoke flask.dev                # Start a development build of Flask, listening on `localhost:4000`, including hot reloading.
invoke web.dev                  # Start a development build of the client, listening on `localhost:3000`, including hot reloading.
```

The web client development instance will then be accessible at `http://localhost:3000/`.

## Installation of Dependencies

Requires a `git` executable.

- On Windows, development has used [Git for Windows](https://gitforwindows.org/).

Requires installation of Javascript and Python dependencies.

### Javascript

For Javascript components, Node.js and the Yarn package manager.

- [Node.js](https://nodejs.org/)

  Installers: <https://nodejs.org/en/download/>
  
  Development has used version 14.x.

- [Yarn](https://yarnpkg.com/)

  ```
  npm install --global yarn
  ```

### Python

For Python components, Python and the Pipenv tool for managing virtual environments and dependencies.

- [Python](https://www.python.org/)

  Development uses version 3.9.x.

  On Windows, specific versions can be installed: <https://www.python.org/downloads/>
  
  On Mac, specific versions are managed using pyenv: <https://github.com/pyenv/pyenv>
  
- [Pipenv](https://pipenv.pypa.io/en/latest/)

  Pipenv manages the creation of a Python virtual environment and pip installation of dependencies in that environment.
    
  Pipenv must be installed in an existing Python installation, typically a global installation:  
    
  ```
  pip install pipenv
  ```
    
  The `pipenv` command is then available in that Python installation. For example:
    
  ```
  pipenv --version
  ```
    
  Depending how a machine manages specific versions of Python, other possibilities for accessing the `pipenv` command include:
    
  - On Windows, using a full path to a specific version installation:
    
    ```
    C:\Python39\Scripts\pip install pipenv
    C:\Python39\Scripts\pipenv --version
    ```  
    
  - On a Mac, Pipenv will detect pyenv and use it to ensure the desired version of Python in the created virtual environment.
    
  With Pipenv installed and access to the `pipenv` command, see [Using Pipenv](#using-pipenv).

## Providing Secrets

Runtime secrets are expected in the `secrets` directory.

- `secrets/server/prod/config.yaml`

  Secret for accessing the production server. Used by:
  
  - `tasks/database.py`: For forwarding the database from the production server.

## Using Pipenv

Ensure Pipenv is installed and the `pipenv` command is accessible, as in [Installation of Dependencies](#installation-of-dependencies):

```
pipenv --version
```

Use the `pipenv` command to create a virtual environment and install the `Pipfile.lock` dependencies, including development dependencies:

```
pipenv sync --dev
```

Activate a shell inside the created virtual environment:

```
pipenv shell
```

On Windows, the `pipenv shell` implementation has some limitations (e.g., lacks command history). You may prefer:

```
pipenv run cmd
```

Within the resulting Pipenv shell, all commands will benefit from dependencies in `Pipefile` and `Pipefile.lock`.
See examples in [Typical Development Environment](#typical-development-environment)
and in [Using Invoke](#using-invoke).
The development dependencies of this project also include Pipenv, 
so the `pipenv` command is available locally (e.g., without a need to reference a specific global installation). 

- To install a new dependency, update versions of all dependencies, and update `Pipefile` and `Pipefile.lock`:

  ```
  pipenv install <package>
  ```

- To install a new development dependency, update versions of all dependencies, and update `Pipefile` and `Pipefile.lock`:

  ```
  pipenv install --dev <package>
  ```

## Using Invoke

This project uses [Invoke](https://www.pyinvoke.org/) for task execution.

Within a Pipenv shell (as in [Using Pipenv](#using-pipenv)), list available tasks:

```
invoke -l
```

For example:

```
Available tasks:

  config.display            Display the Invoke configuration.
  database.forward.prod     Forward the database from our production server, listening on `localhost:8000`.
  dependencies.ensure.dev   Ensure dependencies are installed, including development dependencies.
  flask.dev                 Start a development build of Flask, listening on `localhost:4000`, including hot reloading.
  flask.prod                Start a production build of Flask, listening on `0.0.0.0:4000`.
  web.dev                   Start a development build of the client, listening on `localhost:3000`, including hot reloading.
  web.prod.build            Build a production bundle of the client.
  web.prod.serve            Serve a production bundle of the client, listening on `0.0.0.0:3000`.
```
