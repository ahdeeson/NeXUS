thorlabs_elliptec
=================

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


Support
-------

Documentation can be found online at `<https://thorlabs-elliptec.readthedocs.io/en/latest>`__.

Source code is hosted at `<https://gitlab.com/ptapping/thorlabs-elliptec>`__.

Bug reports, feature requests and suggestions can be submitted to the `issue tracker <https://gitlab.com/ptapping/thorlabs-elliptec/-/issues>`__.


License
-------

This software is free and open source, licensed under the GNU Public License.
See the `LICENSE <https://gitlab.com/ptapping/thorlabs-elliptec/-/blob/main/LICENSE>`__ for details.