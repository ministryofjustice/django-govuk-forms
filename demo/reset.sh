#!/usr/bin/env bash

echo Resetting demo app
cd `dirname $0`
rm -f db.sqlite  # remove DB
rm -rf govuk_template/ static/  # remove old build files
./manage.py startgovukapp govuk_template  # download and build components
./manage.py migrate  # setup db
./manage.py buildscss  # to create all css
./manage.py collectstatic --no-input  # collect built static assets
./manage.py shell --command "
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_superuser(username='admin', email='admin@localhost', password='admin')

from govuk_template_base.models import Link
from govuk_template_base.service_settings import default_settings
service_settings = default_settings()
service_settings.name = 'Demo service'
service_settings.phase = 'alpha'
service_settings.header_links.add(Link.objects.create(name='Simple', link='demo:simple', link_is_view_name=True))
service_settings.header_links.add(Link.objects.create(name='Long', link='demo:long', link_is_view_name=True))
service_settings.header_links.add(Link.objects.create(name='Pre-filled', link='demo:prefilled', link_is_view_name=True))
service_settings.header_links.add(Link.objects.create(name='Field sets', link='demo:fieldsets', link_is_view_name=True))
service_settings.header_links.add(Link.objects.create(name='Conditionally revealed', link='demo:revealing', link_is_view_name=True))
service_settings.save()
"
echo Run demo using "./manage.py runserver" or "./manage.py runserver --settings settings_without_db"
