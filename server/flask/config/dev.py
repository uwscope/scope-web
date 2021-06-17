class Config:
    SECRET_KEY = 'development'

    # Paths should not reference `localhost`, but should instead reference `127.0.0.1`.
    # We have observed name resolution of `localhost` introducing a 2 second delay in development environments.

    # Database is forwarded with a prefix `/db/` through SSH to port 8000
    URI_DATABASE = 'http://127.0.0.1:8000/db/'
