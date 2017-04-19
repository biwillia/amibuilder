#!/usr/bin/env python

from distutils.core import setup

setup(
  name = 'amibuilder',
  packages = ['amibuilder'],
  version = '0.5.2',
  description = 'A utility to build an AMI from a shell script or Dockerfile',
  author = 'Ben Williams',
  author_email = 'hello@flex.io',
  url = 'https://github.com/biwillia/amibuilder',
  download_url = 'https://github.com/biwillia/amibuilder/archive/0.1.tar.gz',
  keywords = ['ec2', 'ami', 'aws', 'dockerfile', 'build' ],
  classifiers = [],
  install_requires = [ 'boto3' ],
  entry_points={
    'console_scripts': [
      'amibuilder=amibuilder.cli:main'
    ]
  }
)
