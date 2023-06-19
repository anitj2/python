# Script to generate QR Code for WI-FI.
# Using the QR Code, directly connect to WI-FI network. Not need to enter password.
# For guests at home, you can create QR code so they can use to connect to guest wi-fi without entering password.

import qrcode

def generate_wifi_qr_code(ssid, password):
    wifi_data = f'WIFI:S:{ssid};T:WPA;P:{password};;'
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(wifi_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img.save("wifi_qr_code.png")  # Save the QR code image to a file

# Usage example
ssid = "<SSID NAME HERE>"
password = "<WIFI Password"
generate_wifi_qr_code(ssid, password)
