"""Small helpers shared by the bench scripts (my_fid, phase_test, offset_test, amp_sweep, noise_test).
 
Nothing here talks to the board; it only processes the arrays that Experiment.run() returns.
"""
import os
import time
import numpy as np
 
 
def find_blocks(y, thresh=0.5, keep=0.6):
    """Find the RF blocks in a complex RX trace.
 
    A block is a run of consecutive samples with |y| > thresh * max|y|.
    Returns a list of (start, stop) index pairs covering only the central
    `keep` fraction of each block, so the CIC-smoothed edges are excluded.
    """
    mag = np.abs(y)
    on = mag > thresh * mag.max()
    edges = np.flatnonzero(np.diff(on.astype(int)))   # indices where on/off changes
    if on[0]:
        edges = np.r_[-1, edges]
    if on[-1]:
        edges = np.r_[edges, len(y) - 1]
    blocks = []
    for a, b in zip(edges[0::2] + 1, edges[1::2] + 1):   # [a, b) is one block
        n = b - a
        cut = int(round(n * (1 - keep) / 2))
        blocks.append((a + cut, b - cut))
    return blocks
 
 
def save_run(name, **arrays):
    """Save arrays to data/<name>_<YYYYmmdd_HHMMSS>.npz and return the path."""
    os.makedirs("data", exist_ok=True)
    path = os.path.join("data", f"{name}_{time.strftime('%Y%m%d_%H%M%S')}.npz")
    np.savez(path, **arrays)
    print("saved", path)
    return path
 
