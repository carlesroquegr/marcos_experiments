"""
Four pulses in one RX window, same amplitude, programmed phase 0, 90,  180, 270 deg.
The cable and front end add an unknown phase phi0 to all of them, so we compare each
block with the first one: angle(b_k/b_0) removes phi0.
"""

import numpy as np
import matplotlib.pyplot as plt

import external
import experiment as ex
from bench_utils import find_blocks, save_run

RUN_ON_BOARD = True
PHASES_DEG = [0, 90, 180, 270]

def phase_test():
    rx_t = 100 / 122.88
    exp = ex.Experiment(lo_freq=20, rx_t=rx_t, init_gpa=False, flush_old_rx=True)

    amp = 0.5

    times, values = [], []
    for k, ph in enumerate(PHASES_DEG):
        t_on = 20 + 60 * k                               # pulses at 20, 80, 140, 200 us
        times += [t_on, t_on + 30]                       # each 30 us long, 30 us gap
        values += [amp * np.exp(1j * np.deg2rad(ph)), 0]
    tx = (np.array(times), np.array(values))
    rx = (np.array([10, 250]), np.array([1, 0]))
    exp.add_flodict({'tx0': tx, 'tx1': tx, 'rx0_en': rx, 'rx1_en': rx})

    if not RUN_ON_BOARD:
        exp.plot_sequence()
        plt.show()
        return

    rxd, msgs = exp.run()
    exp.close_server(only_if_sim=True)

    y = rxd['rx1']
    ts = exp.get_rx_ts()[1]
    t = np.arange(len(y)) * ts

    blocks = find_blocks(y)
    print(f"found {len(blocks)} blocks (expected {len(PHASES_DEG)})")
    means = [y[a:b].mean() for a, b in blocks]
    for k, m in enumerate(means):
        rel = m / means[0]
        print(f"block {k + 1}: programmed {PHASES_DEG[k]:4d} deg | measured relative phase "
              f"{np.rad2deg(np.angle(rel)):7.1f} deg | amplitude ratio {abs(rel):.3f}")
    save_run("phase_test", y=y, ts=ts, phases=np.array(PHASES_DEG))

    plt.plot(t, np.abs(y), 'k', label='|rx1|')
    plt.plot(t, y.real, label='real')
    plt.plot(t, y.imag, label='imag')
    plt.xlabel('time in RX window (us)')
    plt.title('phase_test: 0 / 90 / 180 / 270 deg')
    plt.legend()
    plt.show()


if __name__ == "__main__":
    phase_test()
