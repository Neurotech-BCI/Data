#Yaoyue Wang

import time
import numpy as np
import matplotlib.pyplot as plt
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

# Configuration
SAMPLE_RATE = 250  # Cyton sampling rate (samples per second)
WINDOW_SIZE = 10   # 10 seconds
BUFFER_SIZE = SAMPLE_RATE * WINDOW_SIZE  # Total samples for 10 seconds

# Configure the Cyton board
params = BrainFlowInputParams()
params.serial_port = "ttyusb0"  # Replace with your actual COM port
board_id = BoardIds.CYTON_DAISY_BOARD.value  # Cyton with Daisy module

try:
    # Initialize and start streaming
    BoardShim.enable_board_logger()
    board = BoardShim(board_id, params)
    board.prepare_session()
    board.start_stream()

    print("Streaming data... Press Ctrl+C to stop.")

    # Initialize buffer and plot
    eeg_channels = BoardShim.get_eeg_channels(board_id)
    channel_to_plot = eeg_channels[0]  # Plot the first EEG channel
    rolling_buffer = np.zeros(BUFFER_SIZE)  # Buffer to hold the last 10 seconds of data

    # Set up live plot
    plt.ion()
    fig, ax = plt.subplots()
    x_vals = np.linspace(-WINDOW_SIZE, 0, BUFFER_SIZE)  # Time axis for 10 seconds

    while True:
        # Get latest data from the board
        data = board.get_board_data()  # This fetches all available data
        if data.shape[1] > 0:
            eeg_data = data[channel_to_plot, :]  # Get data for the selected EEG channel

            # Update rolling buffer
            rolling_buffer = np.roll(rolling_buffer, -eeg_data.shape[0])
            rolling_buffer[-eeg_data.shape[0]:] = eeg_data  # Add new data to the buffer

            # Update the plot
            ax.clear()
            ax.plot(x_vals, rolling_buffer, label="Channel 1 (EEG)")
            ax.set_title("Live EEG Signal (Last 10 Seconds)")
            ax.set_xlabel("Time (seconds)")
            ax.set_ylabel("Amplitude (uV)")
            ax.legend()
            plt.pause(0.1)  # Update the plot every 10 ms

except KeyboardInterrupt:
    print("\nStopped streaming.")

finally:
    # Stop streaming and release resources
    board.stop_stream()
    board.release_session()
    print("Session closed.")