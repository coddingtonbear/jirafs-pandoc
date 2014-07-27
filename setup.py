import os
from setuptools import setup, find_packages


requirements_path = os.path.join(
    os.path.dirname(__file__),
    'requirements.txt',
)
try:
    from pip.req import parse_requirements
    requirements = [
        str(req.req) for req in parse_requirements(requirements_path)
    ]
except ImportError:
    requirements = []
    with open(requirements_path, 'r') as in_:
        requirements = [
            req for req in in_.readlines()
            if not req.startswith('-')
            and not req.startswith('#')
        ]


setup(
    name='jirafs-pandoc',
    version='0.9',
    url='https://github.com/coddingtonbear/jirafs-pandoc',
    description=(
        'Automatically convert markup supported by pandoc into PDF/HTML '
        'when uploading to JIRA.'
    ),
    author='Adam Coddington',
    author_email='me@adamcoddington.net',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    install_requires=requirements,
    packages=find_packages(),
    entry_points={
        'jirafs_plugins': [
            'pandoc = jirafs_pandoc:Pandoc',
        ]
    },
)
