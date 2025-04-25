import time
import numpy as np
import pandas as pd
import requests
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

# Configuration
params = BrainFlowInputParams()
params.serial_port = "/dev/ttyUSB0"
board_id = BoardIds.CYTON_DAISY_BOARD.value
upload_url = "https://bci-uscneuro.tech/api/upload"

SAMPLE_RATE = 127
WINDOW_SIZE = 1.0  # seconds
FRAME_SAMPLES = SAMPLE_RATE
# use a buffer ~2× as big so you never miss data
BUFFER_SAMPLES = FRAME_SAMPLES * 2

board = BoardShim(board_id, params)
board.prepare_session()
board.start_stream()
print("Streaming…")

# get the indices of the EEG and timestamp channels
eeg_channels   = BoardShim.get_eeg_channels(board_id)
timestamp_chan = BoardShim.get_timestamp_channel(board_id)

last_ts = -np.inf

try:    
    start_time = time.time()
    while True:
        # 1) grab a sliding window of recent data
        data = board.get_current_board_data(BUFFER_SAMPLES)
        # data.shape == (n_channels, up to BUFFER_SAMPLES)

        timestamps = data[timestamp_chan, :]
        eeg_data   = data[eeg_channels, :]

        # 2) find the first sample strictly newer than last_ts
        newer = timestamps > last_ts
        if not np.any(newer):
            # no new samples yet
            time.sleep(0.02)
            continue

        idx = np.argmax(newer)  # first True index

        # 3) make sure there are at least FRAME_SAMPLES ahead
        if timestamps.size - idx < FRAME_SAMPLES:
            time.sleep(0.02)
            continue

        # 4) slice out exactly FRAME_SAMPLES
        new_ts   = timestamps[idx : idx + FRAME_SAMPLES]
        new_data = eeg_data[:, idx : idx + FRAME_SAMPLES]

        # 5) update last_ts so we never re-process these
        last_ts = new_ts[-1]

        # 6) build and upload CSV
        df = pd.DataFrame(
            np.column_stack((new_ts, new_data.T)),
            columns=["timestamp"] + [f"CH_{i+1}" for i in range(len(eeg_channels))]
        )
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        headers   = {"Content-Type": "text/csv"}

        resp = requests.post(upload_url, data=csv_bytes, headers=headers, timeout=3.0)
        elapsed_time = time.time() - start_time
        print(f"[{elapsed_time:.2f}s elapsed] Uploaded {FRAME_SAMPLES} samples — Status: {resp.status_code}")

        # stop condition if you like:
        if resp.status_code == 204:
            break

        # 7) throttle so you don’t spin-lock
        time.sleep(WINDOW_SIZE * 0.8)

finally:
    # stop demo
    print("Stopping demo…")
    
    board.stop_stream()
    board.release_session()
    print("Session closed.")
