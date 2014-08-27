#!/bin/bash

coverage run --source='.' manage.py test --settings=gallery.settings.test
