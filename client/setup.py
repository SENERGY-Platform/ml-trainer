#!/usr/bin/env python

import setuptools
setuptools.setup(
      name='model_trainer_client',
      version='2.0.59', # This version must be equal to the git tag in order for pip to recognize updates
      description='Trainer Client',
      author='Hannes Hansen',
      author_email='',
      packages=setuptools.find_packages(),
      python_requires='>=3.5.3',
      install_requires=[
          "requests==2.32.3"
      ]
)