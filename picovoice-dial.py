#!/usr/bin/env python3.6
"""
Use Asterisk EAGI protocol and Picovoice to process voice commands.

Caller can say "hey asterisk dial X" where X is a single digit integer and Asterisk will dial the extension
into the call.

When running Asterisk in the foreground with `asterisk -vvvvgc`, stderr from this script goes to the console. We
assume the audio stream is 16-bit 8000 Hz.

It requires 3 files in the current working directory:

* picovoice.key- contains your Picovoice key. Remember to chown to asterisk:asterisk and chmod 600.
* hey-asterisk_en_linux_v3_0_0.ppn
* asterisk-dial_en_linux_v3_0_0.rhn

This is a proof of concept. A production version would need better error handling, logging, more flexible
configuration, not requiring assuming the service is Python 3.6, and handling of AGI messages in various states.
"""
import sys
from picovoice import Picovoice
import syslog
import os
import struct
import resampy
import numpy as np

os.chdir('/var/lib/asterisk/agi-bin/')

with open('picovoice.key') as key:
    picovoice_key = key.read().strip()

keyword_path = "hey-asterisk_en_linux_v3_0_0.ppn"
context_path = "asterisk-dial_en_linux_v3_0_0.rhn"

SAMPLE_SIZE_BYTES = 2  # 16 bit audio
SAMPLE_RATE = 8000
AUDIO_FILE_DESCRIPTOR = 3  # By Asterisk convention


def bytes_to_int16(byte_data):
    """Unpack the bytes as little-endian signed short integers."""
    return struct.unpack('<h', byte_data)[0]


def resample(samples, new_rate):
    """Return samples, resampled to new_rate."""
    resampled = resampy.resample(samples, SAMPLE_RATE, new_rate)
    resampled_orig_type = resampled.astype(samples.dtype)
    return resampled_orig_type


def wake_word_callback():
    syslog.syslog(syslog.LOG_INFO, 'wake_word_callback')


def inference_callback(inference):
    syslog.syslog(syslog.LOG_INFO, 'inference_callback {}'.format(inference))
    if inference.is_understood and inference.intent == 'dialExtension':
        extension = int(inference.slots['extension'])
        dial_extension(extension)


def dial_extension(extension):
    """Send a command to dial the given extension and wait for the response."""
    syslog.syslog(syslog.LOG_INFO, 'dialing {}'.format(extension))
    sys.stdout.write('EXEC Dial SIP/{},30\n'.format(extension))
    sys.stdout.flush()
    response = sys.stdin.readline().strip()
    syslog.syslog(syslog.LOG_INFO, response)


def main():
    picovoice = Picovoice(
        access_key=picovoice_key,
        keyword_path=keyword_path,
        wake_word_callback=wake_word_callback,
        context_path=context_path,
        inference_callback=inference_callback
    )

    audio = None
    try:
        audio = os.fdopen(AUDIO_FILE_DESCRIPTOR, 'rb')
        # The number of bytes to read is the sample size multiplied by the number of samples Picovoice wants in a 
        # frame, except we adjust for how the number of samples will change after resampling.
        frame_length_before_resampling = picovoice.frame_length // (picovoice.sample_rate // SAMPLE_RATE)
        read_bytes = SAMPLE_SIZE_BYTES * frame_length_before_resampling
        while True:
            # Read audio forever
            audio_data = audio.read(read_bytes)
            samples = []
            sample_count = 0
            while sample_count < frame_length_before_resampling:
                start = sample_count * SAMPLE_SIZE_BYTES
                sample = audio_data[start:start+2]
                samples.append(bytes_to_int16(sample))
                sample_count += 1

            resampled = resample(np.array(samples), picovoice.sample_rate)
            picovoice.process(resampled)
    except Exception as e:
        # Catch anything, log it, and exit.
        syslog.syslog(syslog.LOG_ERR, str(e))
        sys.exit(1)
    finally:
        audio.close()

    picovoice.delete()


if __name__ == '__main__':
    syslog.syslog(syslog.LOG_INFO, 'Starting picovoice-dial.py')
    main()
