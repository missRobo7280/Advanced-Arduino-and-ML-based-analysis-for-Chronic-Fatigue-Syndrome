import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd
import threading
import serial
import time
import joblib
import re

model = joblib.load("random_forest_model.pkl")
scaler = joblib.load("scaler.pkl")
le = joblib.load("label_encoder.pkl")
feature_names = joblib.load("feature_names.pkl")  # ['Altitude', 'GSR', 'Pressure', 'Pulse', 'Temp']


ser = serial.Serial('COM8', 9600, timeout=2)
time.sleep(2)


class SensorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Arduino based Stress Analysis System for Chronic Fatigue Syndrome(CFS)")
        self.root.configure(bg="black")
        self.running = False

        self.data = {"GSR": [], "Pulse": [], "Temp": [], "Pressure": [], "Altitude": []}

        self.create_widgets()
        self.plot_setup()

    def create_widgets(self):
        self.title_label = tk.Label(self.root, text="Live Stress Prediction", font=("Helvetica", 18, "bold"), fg="white", bg="black")
        self.title_label.pack(pady=10)

        self.prediction_label = tk.Label(self.root, text="Prediction: --", font=("Helvetica", 16), fg="white", bg="black")
        self.prediction_label.pack(pady=10)

        self.button_frame = tk.Frame(self.root, bg="black")
        self.button_frame.pack(pady=10)

        self.start_button = ttk.Button(self.button_frame, text="Start", command=self.start_reading)
        self.start_button.grid(row=0, column=0, padx=10)

        self.stop_button = ttk.Button(self.button_frame, text="Stop", command=self.stop_reading)
        self.stop_button.grid(row=0, column=1, padx=10)

        self.canvas_frame = tk.Frame(self.root, bg="black")
        self.canvas_frame.pack()

    def plot_setup(self):
        self.figures = {}
        self.axes = {}
        self.canvases = {}
        sensors = ["GSR", "Pulse", "Temp", "Pressure", "Altitude"]

        for i, sensor in enumerate(sensors):
            fig, ax = plt.subplots(figsize=(4, 2), dpi=100)
            fig.patch.set_facecolor("black")
            ax.set_facecolor("black")
            ax.tick_params(colors='white', labelsize=8)
            ax.spines[:].set_color("white")
            ax.set_title(sensor, color='white')

            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas.get_tk_widget().grid(row=i // 2, column=i % 2, padx=10, pady=5)

            self.figures[sensor] = fig
            self.axes[sensor] = ax
            self.canvases[sensor] = canvas

    def update_graphs(self):
        for sensor in self.data:
            self.axes[sensor].clear()
            self.axes[sensor].set_title(sensor, color='white')
            self.axes[sensor].set_facecolor('black')
            self.axes[sensor].tick_params(colors='white')
            self.axes[sensor].plot(self.data[sensor], color='cyan')
            self.axes[sensor].set_xlim(0, 50)
            self.canvases[sensor].draw()

    def read_sensor_data(self):
        while self.running:
            try:
                ser.write(b"A")
                time.sleep(1)
                raw = ser.readline().decode().strip()
                print(f"📥 Received: {raw}")

                if not raw:
                    continue

                values = re.findall(r"[-+]?\d*\.\d+|\d+", raw)
                if len(values) < 5:
                    continue

                gsr = float(values[0])
                pulse = float(values[1])
                temp = float(values[2])
                pressure = float(values[3])
                altitude = float(values[4])

                for key, val in zip(["GSR", "Pulse", "Temp", "Pressure", "Altitude"],
                                    [gsr, pulse, temp, pressure, altitude]):
                    self.data[key].append(val)
                    if len(self.data[key]) > 50:
                        self.data[key].pop(0)

                input_df = pd.DataFrame([[altitude, gsr, pressure, pulse, temp]], columns=feature_names)
                scaled = scaler.transform(input_df)

                if gsr<300:
                    result = "Abnormal"
                    color="red"
                    ser.write(b"C")
                elif gsr > 300 or pulse <800:
                    result = "Normal"
                    color = "green"
                    ser.write(b"B")

                else:
                    pred = model.predict(scaled)[0]
                    result = le.inverse_transform([pred])[0]
                    color = "green" if result == "Normal" else "red"
                    ser.write(b"B") if result == "Normal" else ser.write(b"C")

                self.prediction_label.config(text=f"Prediction: {result}", fg=color)
                self.update_graphs()

            except Exception as e:
                print(f"❌ Error: {e}")

            time.sleep(2)

    def start_reading(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.read_sensor_data, daemon=True).start()

    def stop_reading(self):
        self.running = False
        self.prediction_label.config(text="Prediction: --", fg="white")

# Start GUI
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = SensorApp(root)
        root.mainloop()
    finally:
        if ser.is_open:
          ser.close()

