import serial
import time
import pandas as pd
import os
import re

# Serial configuration
com_port = "COM8"
baud_rate = 9600
excel_file = "sensor_values_abnormal_live.xlsx"

# Set column names (in the order they appear)
columns = ["GSR", "Pulse", "Temp", "Pressure", "Altitude"]

# Load existing data or create new DataFrame
if os.path.exists(excel_file):
    df = pd.read_excel(excel_file)
else:
    df = pd.DataFrame(columns=columns)

try:
    ser = serial.Serial(com_port, baud_rate, timeout=2)
    print(f"Connected to {com_port} at {baud_rate} baud")
    time.sleep(2)

    while True:
        ser.write(b'A')
        print("Sent: A")
        time.sleep(1)

        if ser.in_waiting > 0:
            data = ser.readline()
            try:
                decoded_data = data.decode("utf-8", errors="ignore").strip()
            except UnicodeDecodeError:
                decoded_data = data.decode("latin-1", errors="ignore").strip()

            if decoded_data:
                print("Received:", decoded_data)

                # Extract all numeric values (integer or float)
                values = re.findall(r"[-+]?\d*\.\d+|\d+", decoded_data)

                if len(values) == 5:
                    # Convert strings to float or int
                    parsed_values = [float(v) if '.' in v else int(v) for v in values]
                    # Append to DataFrame
                    df = pd.concat([df, pd.DataFrame([parsed_values], columns=columns)], ignore_index=True)
                    # Save to Excel
                    df.to_excel(excel_file, index=False)

        time.sleep(2)

except serial.SerialException as e:
    print(f"Serial Error: {e}")

except KeyboardInterrupt:
    print("\nExiting program...")

finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial connection closed.")
