import numpy as np


def trainola(a, b):
    # Compute trainola score for two waveforms a and b.

    # a and b are 2-D arrays with the same number of rows,
    # but they do not need to have the same number of columns.

    # Returns a score within [0, infinity] such that
    # 0 indicates a match, 1 indicates no correlation,
    # and infinity indicates negative correlation

    a = a.reshape((-1, a.shape[-1]))
    b = b.reshape((-1, b.shape[-1]))

    max_length = max(a.shape[-1], b.shape[-1])

    # Probably can cache these somehow (outside of the function)
    max_length_2 = int(2**np.ceil(np.log2(max_length)))
    A = np.fft.fft(a, n=max_length_2)
    B = np.fft.fft(b, n=max_length_2)
    circular_corr = np.fft.ifft(A * B.conj()).real
    corr_scores = np.sum(circular_corr / (max(np.linalg.norm(a), np.linalg.norm(b)) ** 2), axis=0)
    mapped_scores = mapping(corr_scores)
    return max(min(mapped_scores), 0)


def mapping(x):
    # 0 is good, 1 is neutral, inf is bad

    # fix for floating point
    x_shifted = x + 1
    close_to_zero = np.isclose(x_shifted, 0)
    x_shifted[close_to_zero] = 0

    with np.errstate(divide='ignore'):
        return np.divide(2, x_shifted) - 1
