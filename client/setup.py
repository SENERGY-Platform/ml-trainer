#!/usr/bin/env python

import setuptools
setuptools.setup(
      name='model_trainer_client',
      version='2.2.75',
      description='Trainer Client',
      author='Hannes Hansen',
      author_email='',
      packages=setuptools.find_packages(),
      python_requires='>=3.5.3',
      install_requires=[
          "requests==2.32.3"
      ]
)