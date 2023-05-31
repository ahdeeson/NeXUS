Welcome to thorlabs_elliptec's documentation!
===============================================

This is a python interface to Thorlabs Elliptec series of piezoelectric motion stages and mounts. It
should support all models including:

- Thorlabs Elliptec ELL6 shutter
- Thorlabs Elliptec ELL7 linear stage
- Thorlabs Elliptec ELL8 rotation stage
- Thorlabs Elliptec ELL9 multi-position filter mount
- Thorlabs Elliptec ELL10 linear stage
- Thorlabs Elliptec ELL14 rotation mount
- Thorlabs Elliptec ELL17 linear stage
- Thorlabs Elliptec ELL18 rotation stage
- Thorlabs Elliptec ELL20 linear stage

As of version 1.0, all basic functionality is implemented. However, the "multi-drop" capability
which allow multiple devices to share a single serial port device is not yet implemented. This means
that to control more than one device, each device must be connected via its own serial port (such as
a dedicated USB to serial adaptor). The multi-drop feature is planned, and hopefully will be
implemented soon in a future release.

Source code is at `<https://gitlab.com/ptapping/thorlabs-elliptec>`__.

Python Package Index (pypi) page at `<https://pypi.org/project/thorlabs-elliptec>`__.

Documentation online at `<https://thorlabs-elliptec.readthedocs.io>`__.

User Guide
----------

.. toctree::
   :maxdepth: 1

   gettingstarted
   usage
   history

API Documentation
-----------------
.. toctree::
   :maxdepth: 5
   :titlesonly:

   api/thorlabs_elliptec

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
