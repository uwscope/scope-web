import setuptools

setuptools.setup(
    name="scope",
    # Should follow Semantic Versioning <https://semver.org/>
    version="0.0.1",
    # author="",
    # author_email="",
    packages=setuptools.find_packages(),
    url="https://github.com/uwscope/",
    # license="",
    # description="",
    # long_description="",
    python_requires=">=3",
    install_requires=[
        "boto3",
        "cryptography",
        "pyjwt",
        "pymongo",
        "pytz",
        # pyzipper is used in populate scripts
        "pyzipper",
        "requests",
        "ruamel.yaml",
        # jschon is active and < 1.0,
        # pin a specific version to prevent breaking changes
        "jschon==0.8.3",
        "python-dateutil",
        "faker",  # TODO: To remove, used only in development
        "lorem",  # TODO: To remove
        "numpy",  # TODO: To remove
    ],
)
