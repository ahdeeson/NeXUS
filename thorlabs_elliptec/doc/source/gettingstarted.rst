Getting Started
===============

Prerequisites
-------------

The only dependency for thorlabs_elliptec is the python serial library
(`pyserial <https://pypi.org/project/pyserial/>`_) which should be installed automatically if using pip or similar.
If obtaining the code by other means, ensure it is installed and can be found in your python path.

Installing the Software
-----------------------

Download Using Pip
^^^^^^^^^^^^^^^^^^

The package installer for Python (pip) is the typical method for installation:

.. code-block:: sh

    pip install --user --upgrade thorlabs-elliptec

The ``--user`` parameter installs using user-level permissions, thus does not require root or administrator privileges.
To install system wide, remove the ``--user`` parameter and prefix the command with ``sudo`` (Linux, MacOS), or run as administrator (Windows).

Clone From Git
^^^^^^^^^^^^^^

Alternatively, the latest version can be downloaded from the git repository:

.. code-block:: sh

    git clone https://gitlab.com/ptapping/thorlabs-elliptec.git

and optionally installed to your system using ``pip``:

.. code-block:: sh

    pip install --user ./thorlabs-elliptec



