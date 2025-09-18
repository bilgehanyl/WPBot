# WPBot - WhatsApp Bulk Sender

A Python application for sending bulk WhatsApp messages with both GUI and command-line interfaces. WPBot supports Turkish phone number normalization and offers both traditional and single-tab Selenium-based sending modes.

## Features

- **Dual Interface**: GUI and command-line support
- **Bulk Messaging**: Send messages to multiple recipients from a text file
- **Multi-Country Number Support**: Automatic normalization for 40+ countries
- **Two Sending Modes**:
  - Traditional mode using pywhatkit (opens new tabs)
  - Single-tab mode using Selenium (more efficient)
- **Number Validation**: Validates phone numbers in E.164 format
- **Recipients Preview**: Preview and normalize numbers before sending
- **Flexible Message Input**: Type messages directly or load from file
- **Country Selection**: Choose normalization rules for different countries

## Installation

### Prerequisites

- Python 3.8 or higher
- Google Chrome browser
- WhatsApp Web access

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Manual Installation

If you prefer to install dependencies manually:

```bash
pip install pywhatkit selenium webdriver-manager
```

## Usage

### GUI Mode (Recommended for beginners)

Simply run the application without arguments:

```bash
python wpbot.py
```

Or explicitly launch GUI:

```bash
python wpbot.py --gui
```

### Command Line Mode

```bash
python wpbot.py --recipients recipients.txt --message "Your message here"
```

#### Command Line Options

- `--recipients`: Path to text file with phone numbers (one per line)
- `--message`: Message text to send
- `--message-file`: Path to text file containing the message
- `--wait`: Seconds to wait for WhatsApp Web to load (default: 40)
- `--close-time`: Seconds to wait before closing tab (default: 3)
- `--keep-tab-open`: Keep WhatsApp tab open after sending
- `--gui`: Launch GUI interface

## Phone Number Format

### Supported Countries

WPBot supports number normalization for 40+ countries including:

- **Turkey**: `+90`, `90`, `05`, `5` patterns
- **United States**: `+1`, `1` patterns  
- **United Kingdom**: `+44`, `44`, `07` patterns
- **Germany**: `+49`, `49`, `01` patterns
- **France**: `+33`, `33`, `06`, `07` patterns
- **And many more...**

### Supported Formats

The application supports various phone number formats depending on the selected country:

**Turkish numbers:**
- `+905551234567` (E.164 format)
- `905551234567` (without +)
- `05551234567` (Turkish format with 0)
- `5551234567` (Turkish format without country code)

**US numbers:**
- `+1234567890` (E.164 format)
- `1234567890` (without +)

**UK numbers:**
- `+44123456789` (E.164 format)
- `44123456789` (without +)
- `07123456789` (UK mobile format)

### Recipients File Format

Create a text file with one phone number per line:

```
+905551234567
+905559876543
# This is a comment and will be ignored
+905551111111
```

## Examples

### Example Recipients File (`recipients.txt`)

```
+905551234567
+905559876543
+905551111111
```

### Example Message File (`message.txt`)

```
Hello! This is a bulk message from WPBot.
Thank you for your attention.
```

### Command Line Examples

```bash
# Send message to recipients from file
python wpbot.py --recipients recipients.txt --message "Hello World!"

# Send message from file
python wpbot.py --recipients recipients.txt --message-file message.txt

# Keep tabs open after sending
python wpbot.py --recipients recipients.txt --message "Hello!" --keep-tab-open

# Custom wait times
python wpbot.py --recipients recipients.txt --message "Hello!" --wait 60 --close-time 5
```

## GUI Features

1. **Recipients Selection**: Browse and select recipients file
2. **Country Selection**: Choose normalization rules for different countries
3. **Number Normalization**: Automatically convert numbers to E.164 format based on selected country
4. **Recipients Preview**: See all numbers before sending
5. **Message Editor**: Type or paste your message
6. **Options Configuration**: Set wait times and tab behavior
7. **Single-tab Mode**: Use Selenium for more efficient sending
8. **Real-time Logging**: Monitor sending progress

## Sending Modes

### Traditional Mode (Default)
- Uses pywhatkit library
- Opens new browser tab for each recipient
- More reliable but slower
- Better for small batches

### Single-tab Mode (Selenium)
- Uses Selenium WebDriver
- Keeps one browser tab open
- More efficient for large batches
- Requires Chrome browser

## Troubleshooting

### Common Issues

1. **ImportError: pywhatkit not installed**
   ```bash
   pip install pywhatkit
   ```

2. **Selenium not available**
   ```bash
   pip install selenium webdriver-manager
   ```

3. **ChromeDriver issues**
   - The application uses webdriver-manager to auto-download ChromeDriver
   - Ensure Google Chrome is installed

4. **WhatsApp Web not loading**
   - Check your internet connection
   - Ensure WhatsApp Web is accessible
   - Try increasing the wait time

### Performance Tips

- Use single-tab mode for large batches (100+ recipients)
- Increase wait time if you have a slow internet connection
- Close other browser tabs to free up memory
- Use a stable internet connection

## Security and Privacy

- Phone numbers are processed locally
- No data is sent to external servers
- WhatsApp Web is used for sending (same as manual sending)
- Respect WhatsApp's terms of service
- Use responsibly and ethically

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and legitimate business purposes only. Users are responsible for complying with WhatsApp's terms of service and applicable laws. The authors are not responsible for any misuse of this software.
