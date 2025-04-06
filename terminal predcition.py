import serial
import time
import re
import pandas as pd
import joblib

# Load the trained model and supporting tools
model = joblib.load("random_forest_model.pkl")
scaler = joblib.load("scaler.pkl")
le = joblib.load("label_encoder.pkl")
feature_names = joblib.load("feature_names.pkl")  # ['Altitude', 'GSR', 'Pressure', 'Pulse', 'Temp']

# Setup serial communication
ser = serial.Serial('COM8', 9600, timeout=2)
time.sleep(2)
print("🔁 Reading and predicting from Arduino. Press Ctrl+C to stop.\n")

try:
    while True:
        ser.write(b"A")  # Send 'A' to request data
        time.sleep(1)
        raw = ser.readline().decode().strip()
        print(f"📥 Received: {raw}")

        if not raw:
            print("⚠️ Empty input.\n")
            continue

        try:
            # Extract values: GSR, Pulse, Temp, Pressure, Altitude
            values = re.findall(r"[-+]?\d*\.\d+|\d+", raw)
            if len(values) < 5:
                print(f"⚠️ Incomplete values: {values}\n")
                continue

            gsr = float(values[0])
            pulse = float(values[1])
            temp = float(values[2])
            pressure = float(values[3])
            altitude = float(values[4])

            # Prepare data in required order
            data_dict = {
                "Altitude": altitude,
                "GSR": gsr,
                "Pressure": pressure,
                "Pulse": pulse,
                "Temp": temp
            }

            input_df = pd.DataFrame([[data_dict[feat] for feat in feature_names]], columns=feature_names)
            scaled = scaler.transform(input_df)

            # Manual override: Force 'Abnormal' if GSR < 300
            if gsr < 300:
                result = "Abnormal "
            else:
                pred = model.predict(scaled)[0]
                result = le.inverse_transform([pred])[0]

            print(f"✅ Prediction: {result}\n")

        except Exception as e:
            print(f"❌ Error during parsing or prediction: {e}\n")

        time.sleep(2)

except KeyboardInterrupt:
    print("\n⛔ Stopped by user.")
finally:
    ser.close()
    print("🔌 Serial connection closed.")
