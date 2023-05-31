Usage
=====

The device needs to be connected to the host computer via a RS232 style serial connection, for
example, by using a USB to serial adaptor. The interface board supplied with the "kit" form is
essentially just such a device. The first task is to discover which port the device is connected to.
A utility function is provided to list the serial port devices available on the host.

.. code-block:: python

    from thorlabs_elliptec import ELLx, ELLError, ELLStatus, list_devices
    print(list_devices())
    # Prints something like:
    # device=/dev/ttyUSB1, manufacturer=Prolific Technology Inc., product=USB-Serial Controller, vid=0x067b, pid=0x2303, serial_number=None, location=1-1.1

In this example, only a single port is available, so there is no issues with selecting the correct
port. The device can be found automatically:

.. code-block:: python

    stage = ELLx()
    print(f"{stage.model_number} #{stage.device_id} on {stage.port_name}, serial number {stage.serial_number}, status {stage.status.description}")
    # Prints something like:
    # ELL14 #0 on /dev/ttyUSB1, serial number 11400590, status ok

To be more selective with the port selection, several initialisation parameters are available. These
are the same as those described in :meth:`~thorlabs_elliptec.find_device`:

.. code-block:: python

    stage = ELLx(vid=0x067b, pid=0x2303)
    print(f"{stage.model_number} on {stage.port_name}, serial number {stage.serial_number}, status {stage.status.description}")
    # Prints something like:
    # ELL14 on /dev/ttyUSB1, serial number 11400590, status ok

To require a particular model number or serial number of the device, parameters are also available:

.. code-block:: python

    stage = ELLx(x=14, device_serial=123456789)
    # Raises an exception:
    # RuntimeError: Device does not have expected serial number '123456789'! (device reported '11400590')

Once the device is initialised, controlling it is straightforward:

.. code-block:: python

    # Move device to the home position
    stage.home()
    # Movements are in real units appropriate for the device (degrees, mm).
    stage.move_absolute(45.0)
    # The raw device encoder units can also be used with the move raw variants.
    stage.move_absolute_raw(23456)

    # By default, move commands are asynchronous (non-blocking) and return immediately,
    # but you can manually wait for it to be in position
    stage.move_absolute(45.0)
    stage.wait()
    stage.move_relative(-12.34)
    # or test whether movement is still in progress.
    print(stage.is_moving())
    stage.wait()
    print(stage.is_moving())
    print(f"{stage.get_position()}{stage.units}")
    # Prints something like:
    # True
    # False
    # 32.655°

    # Synchronous behaviour can also be achieved by setting the blocking=True parameter,
    # which will perform the wait before returning from each movement command.
    stage.home(blocking=True)
    stage.move_absolute(1.23, blocking=True)
    stage.move_relative(-0.98, blocking=True)

    # When using the synchronous behaviour, any error during movement will raise an exception.
    try:
        stage.move_absolute(-9999)
    except ELLError as ex:
        if ex.status == ELLStatus.OUT_OF_RANGE:
            # Requested move beyond device limits
            print("Device can't move there!")
        else:
            # Other error, eg stage held or blocked so it can't move
            print(f"Movement error: {ex}")
    else:
        print("Move completed OK")

    # When using asynchronous calls, any errors won't have been detected yet,
    # so instead, the is_moving() and wait() methods can raise the exception instead.
    stage.move_relative(300)
    try:
        print(stage.is_moving(raise_errors=True))
        stage.wait(raise_errors=True)
        print(stage.is_moving(raise_errors=True))
    except ELLError as ex:
        print(f"Movement error: {ex}")

    # Once done with the device, it can be specifically closed. Commands to the stage will no
    # longer work until the device is re-initialised.
    stage.close()

See the API documentation for further details on each available command.