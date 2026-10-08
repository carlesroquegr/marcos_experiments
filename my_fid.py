import numpy as np
import matplotlib.pyplot as plt

import external            # must come before experiment: adds ~/marcos/marcos_client to the path
import experiment as ex

RUN_ON_BOARD = False       # False: only draw the sequence. True: send it to the SDRLab.

def my_fid():
    rx_period = 100                    # CIC decimation
    rx_t = rx_period / 122.88          # 0.814 us between RX samples

    exp = ex.Experiment(lo_freq=20, rx_t=rx_t, init_gpa=False, flush_old_rx=True)

    # Timing table (us from sequence start)
    tx = (np.array([20, 50]),  np.array([0.5, 0]))   # RF pulse 20-50 us, amplitude 0.5
    rx = (np.array([10, 210]), np.array([1, 0]))     # RX window 10-210 us

    exp.add_flodict({'tx0': tx, 'tx1': tx, 'rx0_en': rx, 'rx1_en': rx})

    if not RUN_ON_BOARD:
        exp.plot_sequence()
        plt.show()
        return

    rxd, msgs = exp.run()
    exp.close_server(only_if_sim=True)

    y = rxd['rx1']                     # IN2 (loopback from OUT2)
    t = np.arange(len(y)) * rx_t
    print("samples:", len(y), " expected ~", round(200 / rx_t))
    plt.plot(t, np.abs(y), label='|rx1|')
    plt.plot(t, y.real, label='real')
    plt.plot(t, y.imag, label='imag')
    plt.xlabel('time in RX window (us)')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    my_fid()
