from setuptools import setup, find_packages
import sys, os

version = '0.0.1'

setup(name='traumaetranslate',
      version=version,
      description="A traumae translator for the tenyks IRC bot.",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='clients tenyks ircbot services tenyksclient',
      author='Quinlan Pfiffer',
      author_email='qpfiffer@gmail.com',
      url='https://github.com/qpfiffer/traumaetranslate',
      license='LICENSE',
      packages=find_packages('src', exclude=['ez_setup', 'examples', 'tests']),
      package_dir = {'':'src'},
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          'tenyksclient==0.1.24',
          'requests',
      ],
      entry_points={
          'console_scripts': [
              'traumaetranslate = traumaetranslate.main:main',
          ]
      },
      )
