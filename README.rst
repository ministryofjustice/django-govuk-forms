Django GOV.UK Forms
===================

It should be easy to make a Django-based service that follows Government Digital Services’ style guide and reference materials.

This Django app allows forms to be output using the HTML that can be styled using GOV.UK elements.
The styles themselves are provided by another package, https://github.com/ministryofjustice/django-govuk-template

Usage
-----

- Install ``django-govuk-forms`` or ``django-govuk-template[forms]``
- Add ``govuk_forms`` to ``INSTALLED_APPS``

Development
-----------

Please report bugs and open pull requests on `GitHub`_.

Use ``python setup.py test`` to run all tests.

This repository does not need to be updated for every release of GDS’s packages, only breaking changes for overridden components may need fixes.

Distribute a new version by updating the ``VERSION`` tuple in ``govuk_forms`` and run ``python setup.py sdist bdist_wheel upload``.

To do
-----

- Implement basic field styles
- Decide on mechanism for generating the right HTML:
    - Use a form mixin?
    - Use individual widgets?
    - Use templates?
    - Use template tags?

Copyright
---------

Copyright |copy| 2017 HM Government (Ministry of Justice Digital Services). See LICENSE.txt for further details.

.. |copy| unicode:: 0xA9 .. copyright symbol
.. _GitHub: https://github.com/ministryofjustice/django-govuk-forms
