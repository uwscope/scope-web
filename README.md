# scope-web

Core Scope components, including:

- Web client for provider registry in `src`
- Application Server in `server/flask`

## Typical Development Environment

With prerequisites:

- Dependencies installed (as in [Installation of Dependences](#installation-of-dependencies)).
- Secrets provided (as in [Providing Secrets](#providing-secrets))
- Activating a Pipenv shell (as in [Using Pipenv](#using-pipenv)).

```
invoke dependencies.ensure.dev  # Ensure installation of dependencies
invoke database.forward.prod    # Forwards the production database
invoke flask.dev                # Runs the application server, with hot reloading
invoke web.dev                  # Runs the web client, with hot reloading
```

The web client will then be accessible at `http://localhost:3000/`.

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

  Installers: <https://www.python.org/downloads/>
  
  Development has used version 3.9.x.

- [Pipenv](https://pipenv.pypa.io/en/latest/)

  In the root Python environment:

  ```
  pip install pipenv
  ```

## Providing Secrets

Runtime secrets are expected in the `secrets` directory.

- `secrets/server/prod/config.yaml`

  Secret for accessing the production server. Used by:
  
  - `tasks/database.py`: For forwarding the database from the production server.

## Using Pipenv

This project uses [Pipenv](https://pipenv.pypa.io/en/latest/) to manage a virtual environment and dependencies.

Ensure Pipenv is globally installed (as in [Installation of Dependences](#installation-of-dependencies)).

First use Pipenv to create a virtual environment and install the `Pipfile.lock` dependencies, including development dependencies:

```
pipenv sync --dev
```

- On Windows, due to path configuration issues you may need to specify the full `pipenv` path:
  
  ```
  C:\Python39\Scripts\pipenv sync --dev
  ```  

Then activate a shell inside the created environment:

```
pipenv shell
```

- On Windows, the Pipenv shell implementation has some limitations (e.g., lacks command history). You may prefer:

  ```
  pipenv run cmd
  ```
    
- On Windows, due to path configuration issues you may need to specify the full `pipenv` path:
  
  ```
  C:\Python39\Scripts\pipenv run cmd
  ```  

From within the Pipenv shell, all commands will benefit from dependencies in `Pipefile` and `Pipefile.lock`.
See examples commands in [Typical Development Environment](#typical-development-environment)
and in [Using Invoke](#using-invoke).

- To install a new dependency, including updating `Pipefile` and `Pipefile.lock`:

  ```
  pipenv install <package>
  ```

- To install a new development dependency, including updating `Pipefile` and `Pipefile.lock`:

  ```
  pipenv install --dev <package>
  ```

## Using Invoke

This project uses [Invoke](https://www.pyinvoke.org/) for task execution.

List available tasks:

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
