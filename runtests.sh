#!/bin/bash

coverage run --source='.' manage.py test --settings=project.settings.test
