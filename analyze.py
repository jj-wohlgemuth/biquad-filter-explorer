from scipy import signal
import numpy as np


def biquad(eq_type, fs_hz, frequency_hz, gain_db, q):

    '''
    https://www.musicdsp.org/en/latest/_downloads/3e1dc886e7849251d6747b194d482272/Audio-EQ-Cookbook.txt
    '''
    
    A = np.sqrt(10**(gain_db / 20.0))
    Omega = 2.0 * np.pi * (frequency_hz / fs_hz)
    sn = np.sin(Omega)
    cs = np.cos(Omega)
    alpha = sn / (2.0 * q)
    a = np.ones(3, dtype=np.float32)
    b = np.ones(3, dtype=np.float32)

    if eq_type == 'PEAKING':
        b[0] = 1 + alpha * A
        b[1] = -2*cs
        b[2] = 1 - alpha * A
        a[0] = 1 + alpha / A
        a[1] = -2 * cs
        a[2] = 1 - alpha / A

    elif eq_type == 'LOWPASS':
        b[0] = (1 - cs) / 2
        b[1] = 1 - cs
        b[2] = b[0]
        a[0] = 1 + alpha
        a[1] = -2 * cs
        a[2] = 1 - alpha

    elif eq_type == 'HIGHPASS':
        b[0] = (1 + cs) / 2.0
        b[1] = -1 * (1 + cs)
        b[2] = b[0]
        a[0] = 1 + alpha
        a[1] = -2 * cs
        a[2] = 1 - alpha

    elif eq_type == 'BANDPASS_SKIRT':
        b[0] = sn / 2
        b[1] = 0
        b[2] = -b[0]
        a[0] = 1 + alpha
        a[1] = -2 * cs
        a[2] = 1 - alpha

    elif eq_type == 'BANDPASS_PEAK':
        b[0] = alpha
        b[1] = 0
        b[2] = -b[0]
        a[0] = 1 + alpha
        a[1] = -2 * cs
        a[2] = 1 - alpha

    elif eq_type == 'NOTCH':
        b[0] = 1
        b[1] = -2 * cs
        b[2] = b[0]
        a[0] = 1 + alpha
        a[1] = -2 * cs
        a[2] = 1 - alpha

    elif eq_type == 'ALLPASS':
        b[0] = 1 - alpha
        b[1] = -2 * cs
        b[2] = 1 + alpha
        a[0] = 1 + alpha
        a[1] = -2 * cs
        a[2] = 1 - alpha

    elif eq_type == 'LOWSHELF':
        b[0] = A*((A+1) - (A-1)*cs + 2*np.sqrt(A)*alpha)
        b[1] = 2*A*((A-1) - (A+1)*cs)
        b[2] = A*((A+1) - (A-1)*cs - 2*np.sqrt(A)*alpha)
        a[0] = (A+1) + (A-1)*cs + 2*np.sqrt(A)*alpha
        a[1] = -2*((A-1) + (A+1)*cs)
        a[2] = (A+1) + (A-1)*cs - 2*np.sqrt(A)*alpha

    elif eq_type == 'HIGHSHELF':
        b[0] = A*((A+1) + (A-1)*cs + 2*np.sqrt(A)*alpha)
        b[1] = -2*A*((A-1) + (A+1)*cs)
        b[2] = A*((A+1) + (A-1)*cs - 2*np.sqrt(A)*alpha)
        a[0] = (A+1) - (A-1)*cs + 2*np.sqrt(A)*alpha
        a[1] = 2*((A-1) - (A+1)*cs)
        a[2] = (A+1) - (A-1)*cs - 2*np.sqrt(A)*alpha

    else:
        raise Exception('eq_type not supported')

    return b, a


def get_plot_data(eq_type, fs_hz, frequency_hz, gain_db, q):
    b, a = biquad(eq_type, fs_hz, frequency_hz, gain_db, q)
    z, p, _ = signal.tf2zpk(b, a)
    worN = np.logspace(0, 4, num=1024)*(fs_hz/2)/1e4
    frequency_hz, h = signal.freqz(b, a,
                                   worN=worN,
                                   fs=fs_hz,
                                   include_nyquist=False)
    _, gd_samples = signal.group_delay((b, a),
                                       w=worN,
                                       fs=fs_hz)
    amplitude_dB = 20 * np.log10(abs(h))
    angle_deg = np.unwrap(np.angle(h))*(180/np.pi)
    return z, p, b, a, frequency_hz, amplitude_dB, angle_deg, gd_samples
