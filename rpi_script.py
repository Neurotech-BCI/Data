import time
import numpy as np
import pandas as pd
import requests
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

# Configuration
params = BrainFlowInputParams()
params.serial_port = "/dev/cu.usbserial-DM02590G"
board_id = BoardIds.CYTON_DAISY_BOARD.value
upload_url = "https://bci-uscneuro.tech/api/upload"
SAMPLE_RATE = 127
WINDOW_SIZE = 1  # seconds

board = None

try:
    BoardShim.enable_board_logger()
    board = BoardShim(board_id, params)
    board.prepare_session()
    board.start_stream()
    print("Streaming EEG data and uploading every second...")

    eeg_channels = BoardShim.get_eeg_channels(board_id)
    timestamp_channel = BoardShim.get_timestamp_channel(board_id)
    n_samples = SAMPLE_RATE * WINDOW_SIZE

    while True:
        data = board.get_current_board_data(n_samples)

        if data.shape[1] >= n_samples:
            eeg_data = data[eeg_channels, :].T
            timestamps = data[timestamp_channel, :]

            df = pd.DataFrame(
                np.column_stack((timestamps, eeg_data)),
                columns=["timestamp"] + [f"CH_{i+1}" for i in range(len(eeg_channels))]
            )

            csv_bytes = df.to_csv(index=False).encode('utf-8')

            response = requests.post(
                upload_url,
                files={"file": ("eeg_data.csv", csv_bytes, "text/csv")}
            )

            duration = df["timestamp"].iloc[-1] - df["timestamp"].iloc[0]
            print(f"Uploaded {df.shape[0]} samples ({duration:.2f} s) — Status: {response.status_code}")

        time.sleep(1.0)

except KeyboardInterrupt:
    print("\nStopped streaming.")

except Exception as e:
    print(f"Error: {e}")

finally:
    if board is not None:
        board.stop_stream()
        board.release_session()
        print("Session closed.")