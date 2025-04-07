import serial
import time


try:
    ser = serial.Serial('COM8', 9600, timeout=1)
    time.sleep(2)  # Wait for Arduino to reset

    ser.write(b"B")
    print("✅ Sent 'B' to COM8")

    ser.close()
    print("🔌 Serial connection closed.")

except Exception as e:
    print(f"❌ Error: {e}")
