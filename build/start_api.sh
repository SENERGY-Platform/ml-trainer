#!/bin/bash
gunicorn --bind 0.0.0.0:5000 --chdir=model_trainer app:app

