"""Exercise 4: amplitude linearity up to full scale.
 
Seven TRs inside ONE sequence (timing between them is exact), each with a 30 us pulse
of a different amplitude and its own RX window. rxd['rx1'] returns the windows back to
back; we split it by the known number of samples per window.
 
Expected on the board:
- received level vs programmed amplitude: a straight line through ~0
- level/amp roughly constant (~15 in test_rx_scaling units at 20 MHz)
- possible bending (compression) at 0.8-1.0: OUT max 0.5 Vpp meets IN full scale
  0.5 Vpp. Safe: input damage starts at 1 Vpp.
"""
import numpy as np
import matplotlib.pyplot as plt
 
import external
import experiment as ex
from bench_utils import save_run
 
RUN_ON_BOARD = False
AMPS = [0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0]
TR = 300          # us between pulse starts
WIN = (10, 60)    # RX window inside each TR, us (pulse is 20-50)
 
 
def amp_sweep():
    rx_t = 100 / 122.88
    exp = ex.Experiment(lo_freq=20, rx_t=rx_t, init_gpa=False, flush_old_rx=True)
 
    tx_t, tx_v, rx_tt, rx_v = [], [], [], []
    for k, amp in enumerate(AMPS):
        t0 = k * TR
        tx_t += [t0 + 20, t0 + 50];           tx_v += [amp, 0]
        rx_tt += [t0 + WIN[0], t0 + WIN[1]];  rx_v += [1, 0]
    tx = (np.array(tx_t), np.array(tx_v))
    rx = (np.array(rx_tt), np.array(rx_v))
    exp.add_flodict({'tx0': tx, 'tx1': tx, 'rx0_en': rx, 'rx1_en': rx})
 
    if not RUN_ON_BOARD:
        exp.plot_sequence()
        plt.show()
        return
 
    rxd, msgs = exp.run()
    exp.close_server(only_if_sim=True)
 
    y = rxd['rx1']
    ts = exp.get_rx_ts()[1]
    n_win = len(y) // len(AMPS)                          # samples per window
    print(f"total samples {len(y)}, per window {n_win} (expected ~{round((WIN[1] - WIN[0]) / ts)})")
 
    levels = []
    for k in range(len(AMPS)):
        w = y[k * n_win:(k + 1) * n_win]
        t_w = np.arange(n_win) * ts + WIN[0]             # approx. time inside the TR
        centre = (t_w > 27) & (t_w < 43)                 # middle of the 20-50 us pulse
        levels.append(np.abs(w[centre].mean()))
    levels = np.array(levels)
    amps = np.array(AMPS)
 
    gain, offset = np.polyfit(amps[:-2], levels[:-2], 1) # fit on the low amplitudes only
    for a, l in zip(amps, levels):
        print(f"amp {a:4.2f}: level {l:7.3f}  level/amp {l / a:6.2f}  "
              f"deviation from fit {100 * (l - (gain * a + offset)) / (gain * a + offset):+5.1f} %")
    save_run("amp_sweep", y=y, ts=ts, amps=amps, levels=levels)
 
    plt.plot(amps, levels, 'o', label='measured')
    plt.plot(amps, gain * amps + offset, '--', label=f'fit (low amps): {gain:.2f}*a + {offset:.2f}')
    plt.xlabel('programmed amplitude')
    plt.ylabel('received level |rx1|')
    plt.title('amp_sweep: linearity')
    plt.legend()
    plt.show()
 
 
if __name__ == "__main__":
    amp_sweep()
