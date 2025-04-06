import serial
import time

# Connect to COM8 at 9600 baud rate
try:
    ser = serial.Serial('COM8', 9600, timeout=1)
    time.sleep(2)  # Wait for Arduino to reset

    ser.write(b"C")  # Send the character 'C'
    print("✅ Sent 'C' to COM8")

    ser.close()
    print("🔌 Serial connection closed.")

except Exception as e:
    print(f"❌ Error: {e}")
