# Photo Gallery

This is a simple photo gallery powered by Django. The goal is to allow for an
invite-only gallery such as for a family or an organization.

Photos are organized in to albums. Each album has a month and year
associated with it. Each album is also associated with a location.

Individual photos can also be tagged with people.

I created this application as a way to share photos with my family, but
perhaps someone else may find it useful for inspiration.

## Installation

1. Clone this Github repository:

        git clone https://github.com/timster/gallery.git
        cd gallery

2. Install the pre-requisites:

        pip install https://www.djangoproject.com/download/1.7c2/tarball/
        pip install -r requirements.txt

3. Copy the settings template to create your local settings:

        cp gallery/settings_local.template gallery/settings_local.py

4. Edit the local settings file with your settings:

        vi gallery/settings_local.py

5. Create the database and admin user:

        python manage.py syncdb

6. Collect static files:

        python manage.py collectstatic

7. Configure your web server to serve static files from the directory specified
in the local settings file. See the following Django documentation for more info:
[Deploying static files](https://docs.djangoproject.com/en/dev/howto/static-files/deployment/)

6. Launch the application using the built-in runserver, or deploy using gunicorn,
which is the application server of choice:

        gunicorn gallery.wsgi:application

## Screenshots

Here is what it looks like. I tried to make it pretty.

![Oh so pretty photos](http://i.imgur.com/3ydOHoD.jpg)

More screenshots here: [http://imgur.com/a/glSCe](http://imgur.com/a/glSCe)

## Creating Accounts

The gallery uses an authorization code to ensure that only users you invite
will be able to create accounts. The authorization system has two codes
associated with it. The first code (AUTH_CODE_USER) will allow users to create
a read-only account. The second code (AUTH_CODE_ADMIN) will allow users to
create an admin account that can upload photos, modify albums, etc.

If a user enters the AUTH_CODE_ADMIN when creating an account, his account will
be added to the group specified in AUTH_CODE_ADMIN_GROUP setting. If this group
does not exist, it will be created and all permissions from the photos app will
be added to the group.

## Testing

Automated testing is certainly not complete at the moment, but I'm working on it.

[![Build Status](https://travis-ci.org/timster/gallery.svg?branch=master)](https://travis-ci.org/timster/gallery) 
[![Coverage Status](https://coveralls.io/repos/timster/gallery/badge.png)](https://coveralls.io/r/timster/gallery)

## To-Do List

- Add a Years navigation option just like Locations and People.
- Handle uploading of zip files (extract and pull out images).
- Pull exif data out of photos when uploaded.
