import numpy as np
import matplotlib.pyplot as plt

# first create the time signal, which has two frequencies
f_s = 100.0 # Hz  sampling frequency OR #records/1 sec
f = 1.0 # Hz
tFqs = np.array([11,24,17])
tAmps = np.array([5.1,-3.5, .5])
time = np.arange(0.0, 10.0+1/f_s, 1/f_s)

def createWave(fqs, amps):
    #w = np.random.randn(len(time)) #White Noise
    w = np.zeros(len(time))
    for i in range(len(amps)):
        w += amps[i] * np.sin(fqs[i] * 2 * np.pi * f * time)
    return(w)
wave = createWave(tFqs, tAmps)

# apply hann window and take the FFT
win = np.hanning(len(wave))
FFT = np.fft.fft(win * wave)
n = len(FFT)
freq_hanned = np.fft.fftfreq(n, 1/f_s)  
half_n = np.ceil(n/2.0).astype(int)
fft_hanned_half = 2* (2.0 / n) * FFT[:half_n]
freq_hanned_half = freq_hanned[:half_n]
amps = np.abs(fft_hanned_half)

#Find Local maximums from plot
def locMax(ts, thresh = 1):
    inds = np.where([ts[x] - ts[x-1] >= thresh and ts[x] - ts[x+1] >= thresh for x in range(1,len(ts)-1)])[0]
    return(inds + 1)

max_freqs_ind = locMax(amps,0.5/3)


# Plot
plt.plot(freq_hanned_half, np.abs(fft_hanned_half))
for x in max_freqs_ind: plt.axvline(freq_hanned_half[x], color = 'red', lw = .75, linestyle='--')
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")
plt.show()

print("LocMax Freqs: {}".format(freq_hanned_half[max_freqs_ind]))
print("True Freqs: {}".format(tFqs))

print("LocMax Amps: {}".format(amps[max_freqs_ind]))
print("True Amps: {}".format(tAmps))
