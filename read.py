import serial
import time

# Define serial port and baud rate
com_port = "COM8"  # Ensure this matches your device's port
baud_rate = 9600   # Ensure this matches your device's settings

try:
    # Open serial connection
    ser = serial.Serial(com_port, baud_rate, timeout=2)
    print(f"Connected to {com_port} at {baud_rate} baud")

    # Allow time for the device to initialize
    time.sleep(2)

    while True:
        # Send the character 'A' to the serial device
        ser.write(b'A')  # Sending 'A' as a byte
        print("Sent: a")

        time.sleep(1)  # Allow device time to process and respond

        # Read response
        if ser.in_waiting > 0:
            data = ser.readline()

            try:
                # Attempt to decode the received bytes
                decoded_data = data.decode("utf-8", errors="ignore").strip()
            except UnicodeDecodeError:
                decoded_data = data.decode("latin-1", errors="ignore").strip()

            if decoded_data:
                print("Received:", decoded_data)

        # Add a small delay before sending 'A' again
        time.sleep(2)  # Adjust this delay as needed

except serial.SerialException as e:
    print(f"Serial Error: {e}")

except KeyboardInterrupt:
    print("\nExiting program...")

finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial connection closed.")
