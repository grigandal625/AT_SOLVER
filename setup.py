from setuptools import setup, find_packages

import json
import os
import pathlib
import pkg_resources

def read_pipenv_dependencies(fname):
    """Получаем из Pipfile.lock зависимости по умолчанию."""
    filepath = os.path.join(os.path.dirname(__file__), fname)
    with open(filepath) as lockfile:
        lockjson = json.load(lockfile)
        return [dependency for dependency in lockjson.get('default')]

with pathlib.Path('requirements.txt').open() as requirements_txt:
    install_requires = [
        str(requirement)
        for requirement
        in pkg_resources.parse_requirements(requirements_txt)
    ]


if __name__ == '__main__':
    setup(
        name='at-solver',
        version=os.getenv('PACKAGE_VERSION', '0.0.dev0'),
        package_dir={'': 'src'},
        packages=find_packages(where='src'),
        description='AT-TECHNOLOGY universal inference engine AT-SOLVER',
        install_requires=install_requires
    )