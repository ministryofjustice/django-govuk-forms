Django GOV.UK Forms
===================

**This library has not yet been updated to use the new** `Design system`_

It should be easy to make a Django-based service that follows Government Digital Services’ style guide and reference materials.

This Django app allows forms to be output using the HTML that can be styled using GOV.UK elements.
The styles themselves are provided by another package [1]_.

NB: Until version 1.0, there is likely going to be a lot of variation in the api, so it’s a good idea to pin a specific minor version.

Usage
-----

- Install ``django-govuk-forms`` or ``django-govuk-template[forms]``
- Add ``govuk_forms`` to ``INSTALLED_APPS``
- Inherit forms from ``govuk_forms.forms.GOVUKForm`` and use widgets from ``govuk_forms.widgets``

See the demo folder in this repository on `GitHub`_, it is not included in distributions.

Development
-----------

.. image:: https://travis-ci.org/ministryofjustice/django-govuk-forms.svg?branch=master
    :target: https://travis-ci.org/ministryofjustice/django-govuk-forms

Please report bugs and open pull requests on `GitHub`_.

Use ``python setup.py test`` to run all tests.

This repository does not need to be updated for every release of GDS’s packages, only breaking changes for overridden components may need fixes.

If any localisable strings change, run ``python setup.py makemessages compilemessages``.

Distribute a new version to `PyPi`_ by updating the ``VERSION`` tuple in ``govuk_forms`` and run ``python setup.py compilemessages sdist bdist_wheel upload``.

To do
-----

- Is HTML creation mechanic good?

Copyright
---------

Copyright (C) 2018 HM Government (Ministry of Justice Digital Services).
See LICENSE.txt for further details.

.. _Design system: https://design-system.service.gov.uk/
.. _GitHub: https://github.com/ministryofjustice/django-govuk-forms
.. _PyPi: https://pypi.org/project/django-govuk-forms/

.. [1] https://github.com/ministryofjustice/django-govuk-template
