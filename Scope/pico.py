import time
from ctypes import byref, c_byte, c_int16, c_int32, sizeof, c_float

import numpy as np
from picosdk.ps2000 import ps2000
from picosdk.functions import assert_pico2000_ok, adc2mV, mV2adc, assert_pico_ok
from picosdk.PicoDeviceEnums import picoEnum
from picosdk.ps5000a import ps5000a as ps

import matplotlib.pyplot as plt

SAMPLES = 2000
OVERSAMPLING = 1


def get_timebase(device, wanted_time_interval):
    current_timebase = 1

    old_time_interval = None
    time_interval = c_int32(0)
    time_units = c_int16()
    max_samples = c_int32()

    while ps2000.ps2000_get_timebase(
            device.handle,
            current_timebase,
            2000,
            byref(time_interval),
            byref(time_units),
            1,
            byref(max_samples)) == 0 \
            or time_interval.value < wanted_time_interval:

        current_timebase += 1
        old_time_interval = time_interval.value

        if current_timebase.bit_length() > sizeof(c_int16) * 8:
            raise Exception('No appropriate timebase was identifiable')

    return current_timebase - 1, old_time_interval


def channel_set(device, channel, vRange):
    res = ps2000.ps2000_set_channel(
        device.handle,
        picoEnum.PICO_CHANNEL['PICO_CHANNEL_' + channel],
        True,
        picoEnum.PICO_COUPLING['PICO_DC'],
        ps2000.PS2000_VOLTAGE_RANGE['PS2000_' + vRange],
    )
    assert_pico2000_ok(res)


def read_block(device, channel, vRange, samples, timebase_a):
    collection_time = c_int32()

    res = ps2000.ps2000_run_block(
        device.handle,
        samples,
        timebase_a,
        OVERSAMPLING,
        byref(collection_time)
    )
    assert_pico2000_ok(res)

    while ps2000.ps2000_ready(device.handle) == 0:
        time.sleep(0.1)

    times = (c_int32 * samples)()

    buffer_a = (c_int16 * samples)()
    buffer_b = (c_int16 * samples)()

    overflow = c_byte(0)

    res = ps2000.ps2000_get_times_and_values(
        device.handle,
        byref(times),
        byref(buffer_a),
        byref(buffer_b),
        None,
        None,
        byref(overflow),
        2,
        samples,
    )
    assert_pico2000_ok(res)
    channel_a_overflow = (overflow.value & 0b0000_0001) != 0

    ps2000.ps2000_stop(device.handle)

    channel_a_mv = adc2mV(buffer_a, ps2000.PS2000_VOLTAGE_RANGE['PS2000_' + vRange], c_int16(32767))
    channel_b_mv = adc2mV(buffer_b, ps2000.PS2000_VOLTAGE_RANGE['PS2000_' + vRange], c_int16(32767))

    if channel == 'B':
        return np.array(channel_b_mv), times
    return np.array(channel_a_mv), times


def read_block5000(chandle, vRange, channel, samples, timebase):
    chARange = ps.PS5000A_RANGE["PS5000A_" + vRange]
    maxADC = c_int16()
    ps.ps5000aMaximumValue(chandle, byref(maxADC))
    # assert_pico_ok(status["maximumValue"])

    # Set up single trigger
    # handle = c_handle
    # enabled = 1
    source = ps.PS5000A_CHANNEL["PS5000A_CHANNEL_" + channel]
    threshold = int(mV2adc(500, chARange, maxADC))
    # direction = PS5000A_RISING = 2
    # delay = 0 s
    # auto Trigger = 1000 ms
    ps.ps5000aSetSimpleTrigger(chandle, 1, source, threshold, 2, 0, 1)
    # assert_pico_ok(status["trigger"])

    # Set number of pre and post trigger samples to be collected
    preTriggerSamples = samples
    postTriggerSamples = samples
    maxSamples = preTriggerSamples + postTriggerSamples

    # Get timebase information
    # Warning: When using this example it may not be possible to access all Timebases as all channels are enabled by default when opening the scope.
    # To access these Timebases, set any unused analogue channels to off.
    # handle = c_handle
    # timebase = 12
    # noSamples = maxSamples
    # pointer to timeIntervalNanoseconds = ctypes.byref(timeIntervalns)
    # pointer to maxSamples = ctypes.byref(returnedMaxSamples)
    # segment index = 0
    timeIntervalns = c_float()
    returnedMaxSamples = c_int32()
    ps.ps5000aGetTimebase2(chandle, timebase, maxSamples, byref(timeIntervalns),
                           byref(returnedMaxSamples), 0)
    # assert_pico_ok(status["getTimebase2"])

    # Run block capture
    # handle = c_handle
    # number of pre-trigger samples = preTriggerSamples
    # number of post-trigger samples = PostTriggerSamples
    # timebase = 8 = 80 ns (see Programmer's guide for mre information on timebases)
    # time indisposed ms = None (not needed in the example)
    # segment index = 0
    # lpReady = None (using ps5000aIsReady rather than ps5000aBlockReady)
    # pParameter = None
    # print(ps.ps5000aGetMinimumTimebaseStateless())
    ps.ps5000aRunBlock(chandle, preTriggerSamples, postTriggerSamples, timebase, None, 0, None,
                       None)
    # assert_pico_ok(status["runBlock"])

    # Check for data collection to finish using ps5000aIsReady
    ready = c_int16(0)
    check = c_int16(0)
    while ready.value == check.value:
        ps.ps5000aIsReady(chandle, byref(ready))

    # Create buffers ready for assigning pointers for data collection
    bufferAMax = (c_int16 * maxSamples)()
    bufferAMin = (c_int16 * maxSamples)()  # used for downsampling which isn't in the scope of this example

    # Set data buffer location for data collection from channel A
    # handle = c_handle
    source = ps.PS5000A_CHANNEL["PS5000A_CHANNEL_A"]
    # pointer to buffer max = ctypes.byref(bufferAMax)
    # pointer to buffer min = ctypes.byref(bufferAMin)
    # buffer length = maxSamples
    # segment index = 0
    # ratio mode = PS5000A_RATIO_MODE_NONE = 0
    ps.ps5000aSetDataBuffers(chandle, source, byref(bufferAMax),
                             byref(bufferAMin), maxSamples, 0, 0)
    # assert_pico_ok(status["setDataBuffersA"])

    # create overflow loaction
    overflow = c_int16()
    # create converted type maxSamples
    cmaxSamples = c_int32(maxSamples)

    # Retried data from scope to buffers assigned above
    # handle = c_handle
    # start index = 0
    # pointer to number of samples = ctypes.byref(cmaxSamples)
    # downsample ratio = 0
    # downsample ratio mode = PS5000A_RATIO_MODE_NONE
    # pointer to overflow = ctypes.byref(overflow))
    ps.ps5000aGetValues(chandle, 0, byref(cmaxSamples), 0, 0, 0, byref(overflow))
    # assert_pico_ok(status["getValues"])

    # convert ADC counts data to mV
    adc2mVChAMax = adc2mV(bufferAMax, chARange, maxADC)
    adc2mVChAMax = np.array(adc2mVChAMax)

    # Create time data
    time = np.linspace(0, (cmaxSamples.value - 1) * timeIntervalns.value, cmaxSamples.value)

    # plot data from channel A and

    # Stop the scope
    # handle = c_handle
    ps.ps5000aStop(chandle)
    return adc2mVChAMax, time


def channel_set5000(chandle, channel, vRange):
    channelID = ps.PS5000A_CHANNEL["PS5000A_CHANNEL_" + channel]
    # enabled = 1
    coupling_type = ps.PS5000A_COUPLING["PS5000A_DC"]
    chARange = ps.PS5000A_RANGE["PS5000A_" + vRange]
    # analogue offset = 0 V
    ps.ps5000aSetChannel(chandle, channelID, 1, coupling_type, chARange, 0)
