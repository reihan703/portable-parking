import cv2 as cv
import streamlit as st
from pyzbar.pyzbar import decode
import time


class ScanTicket():
    def __init__(self, timeout=10) -> None:
        self.scanned_ticket = ''
        self.running = False
        self.timeout = timeout  # Timeout in seconds


    
    def execute(self):
        cap = cv.VideoCapture(0)
        cap.set(3, 640)
        cap.set(4, 480)
        self.scanned_ticket = ''
        start_time = time.time()
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to capture image")
                    cap.release()
                    cv.destroyAllWindows()
                    break

                for barcode in decode(frame):
                    self.scanned_ticket = barcode.data.decode("utf-8")
                    cap.release()
                    cv.destroyAllWindows()
                    break  # Exit the loop once a barcode is found

                cv.imshow('In', frame)
                if self.scanned_ticket:
                    cap.release()
                    cv.destroyAllWindows()
                    break

                # Check for timeout
                if time.time() - start_time > self.timeout:
                    cap.release()
                    cv.destroyAllWindows()
                    print("Scanning timed out.")
                    break

                if cv.waitKey(1) & 0xFF == ord('q'):
                    cap.release()
                    cv.destroyAllWindows()
                    break
        finally:
            cap.release()
            cv.destroyAllWindows()

        return self.scanned_ticket
