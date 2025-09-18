"""
WPBot - WhatsApp Bulk Sender

A Python application for sending bulk WhatsApp messages with both GUI and command-line interfaces.
Supports Turkish phone number normalization and offers both traditional and single-tab Selenium-based sending modes.

Author: WPBot Team
License: MIT
"""

import argparse
import sys
import time
from pathlib import Path
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from urllib.parse import quote_plus

try:
    import pywhatkit as whatkit
except ImportError as import_error:
    print("pywhatkit is not installed. Install it with: python -m pip install pywhatkit", file=sys.stderr)
    raise

# Country code data for number normalization
COUNTRY_CODES = {
    "Turkey": {"code": "+90", "patterns": ["90", "05", "5"], "description": "Turkish mobile numbers"},
    "United States": {"code": "+1", "patterns": ["1"], "description": "US/Canada numbers"},
    "United Kingdom": {"code": "+44", "patterns": ["44", "07"], "description": "UK mobile numbers"},
    "Germany": {"code": "+49", "patterns": ["49", "01"], "description": "German mobile numbers"},
    "France": {"code": "+33", "patterns": ["33", "06", "07"], "description": "French mobile numbers"},
    "Italy": {"code": "+39", "patterns": ["39", "03"], "description": "Italian mobile numbers"},
    "Spain": {"code": "+34", "patterns": ["34", "06"], "description": "Spanish mobile numbers"},
    "Netherlands": {"code": "+31", "patterns": ["31", "06"], "description": "Dutch mobile numbers"},
    "Belgium": {"code": "+32", "patterns": ["32", "04"], "description": "Belgian mobile numbers"},
    "Switzerland": {"code": "+41", "patterns": ["41", "07"], "description": "Swiss mobile numbers"},
    "Austria": {"code": "+43", "patterns": ["43", "06"], "description": "Austrian mobile numbers"},
    "Poland": {"code": "+48", "patterns": ["48", "05"], "description": "Polish mobile numbers"},
    "Czech Republic": {"code": "+420", "patterns": ["420", "07"], "description": "Czech mobile numbers"},
    "Hungary": {"code": "+36", "patterns": ["36", "06"], "description": "Hungarian mobile numbers"},
    "Romania": {"code": "+40", "patterns": ["40", "07"], "description": "Romanian mobile numbers"},
    "Bulgaria": {"code": "+359", "patterns": ["359", "08"], "description": "Bulgarian mobile numbers"},
    "Greece": {"code": "+30", "patterns": ["30", "06"], "description": "Greek mobile numbers"},
    "Portugal": {"code": "+351", "patterns": ["351", "09"], "description": "Portuguese mobile numbers"},
    "Sweden": {"code": "+46", "patterns": ["46", "07"], "description": "Swedish mobile numbers"},
    "Norway": {"code": "+47", "patterns": ["47", "04"], "description": "Norwegian mobile numbers"},
    "Denmark": {"code": "+45", "patterns": ["45", "02"], "description": "Danish mobile numbers"},
    "Finland": {"code": "+358", "patterns": ["358", "04"], "description": "Finnish mobile numbers"},
    "Russia": {"code": "+7", "patterns": ["7", "08"], "description": "Russian mobile numbers"},
    "China": {"code": "+86", "patterns": ["86", "01"], "description": "Chinese mobile numbers"},
    "Japan": {"code": "+81", "patterns": ["81", "09"], "description": "Japanese mobile numbers"},
    "South Korea": {"code": "+82", "patterns": ["82", "01"], "description": "South Korean mobile numbers"},
    "India": {"code": "+91", "patterns": ["91", "09"], "description": "Indian mobile numbers"},
    "Brazil": {"code": "+55", "patterns": ["55", "01"], "description": "Brazilian mobile numbers"},
    "Mexico": {"code": "+52", "patterns": ["52", "04"], "description": "Mexican mobile numbers"},
    "Argentina": {"code": "+54", "patterns": ["54", "01"], "description": "Argentine mobile numbers"},
    "Australia": {"code": "+61", "patterns": ["61", "04"], "description": "Australian mobile numbers"},
    "New Zealand": {"code": "+64", "patterns": ["64", "02"], "description": "New Zealand mobile numbers"},
    "South Africa": {"code": "+27", "patterns": ["27", "08"], "description": "South African mobile numbers"},
    "Egypt": {"code": "+20", "patterns": ["20", "01"], "description": "Egyptian mobile numbers"},
    "Saudi Arabia": {"code": "+966", "patterns": ["966", "05"], "description": "Saudi mobile numbers"},
    "UAE": {"code": "+971", "patterns": ["971", "05"], "description": "UAE mobile numbers"},
    "Israel": {"code": "+972", "patterns": ["972", "05"], "description": "Israeli mobile numbers"},
    "Iran": {"code": "+98", "patterns": ["98", "09"], "description": "Iranian mobile numbers"},
    "Pakistan": {"code": "+92", "patterns": ["92", "03"], "description": "Pakistani mobile numbers"},
    "Bangladesh": {"code": "+880", "patterns": ["880", "01"], "description": "Bangladeshi mobile numbers"},
    "Thailand": {"code": "+66", "patterns": ["66", "08"], "description": "Thai mobile numbers"},
    "Vietnam": {"code": "+84", "patterns": ["84", "03"], "description": "Vietnamese mobile numbers"},
    "Indonesia": {"code": "+62", "patterns": ["62", "08"], "description": "Indonesian mobile numbers"},
    "Malaysia": {"code": "+60", "patterns": ["60", "01"], "description": "Malaysian mobile numbers"},
    "Singapore": {"code": "+65", "patterns": ["65", "08"], "description": "Singaporean mobile numbers"},
    "Philippines": {"code": "+63", "patterns": ["63", "09"], "description": "Filipino mobile numbers"},
}

# Optional Selenium import for single-tab mode
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    # WebDriver manager to auto-resolve ChromeDriver
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service as ChromeService
        WEBDRIVER_MANAGER_AVAILABLE = True
    except Exception:
        WEBDRIVER_MANAGER_AVAILABLE = False
    SELENIUM_AVAILABLE = True
except Exception:
    SELENIUM_AVAILABLE = False


def read_recipients_from_file(file_path: Path) -> list[str]:
    """Read phone numbers from a text file, one per line.

    Args:
        file_path: Path to the text file containing phone numbers.

    Returns:
        List of valid phone numbers in E.164 format.

    Raises:
        FileNotFoundError: If the recipients file doesn't exist.

    Note:
        - Ignores empty lines and lines starting with '#'
        - Trims whitespace
        - Basic validation: must start with '+' and contain only '+' and digits
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Recipients file not found: {file_path}")

    recipients: list[str] = []
    with file_path.open("r", encoding="utf-8") as file_handle:
        for raw_line in file_handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if not (line.startswith("+") and line.replace("+", "").isdigit()):
                print(f"Skipping invalid phone entry: {line}", file=sys.stderr)
                continue
            recipients.append(line)
    return recipients


def read_message(message: str | None, message_file: Path | None) -> str:
    """Read message from string or file.

    Args:
        message: Direct message string.
        message_file: Path to file containing the message.

    Returns:
        The message text to send.

    Raises:
        ValueError: If both message and message_file are provided, or neither.
        FileNotFoundError: If message file doesn't exist.
    """
    if message and message_file:
        raise ValueError("Provide either --message or --message-file, not both.")
    if message_file:
        if not message_file.exists():
            raise FileNotFoundError(f"Message file not found: {message_file}")
        return message_file.read_text(encoding="utf-8").strip()
    if not message:
        raise ValueError("A message is required. Use --message or --message-file.")
    return message


def send_messages_to_recipients(
    recipients: list[str],
    message: str,
    per_send_wait_seconds: int,
    tab_close: bool,
    close_time_seconds: int,
) -> None:
    """Send messages to multiple recipients using pywhatkit.

    Args:
        recipients: List of phone numbers in E.164 format.
        message: Message text to send.
        per_send_wait_seconds: Seconds to wait for WhatsApp Web to load.
        tab_close: Whether to close the tab after sending.
        close_time_seconds: Seconds to wait before closing the tab.
    """
    if not recipients:
        print("No valid recipients found.")
        return

    print(f"Starting to send message to {len(recipients)} recipient(s)...")
    for index, phone_number in enumerate(recipients, start=1):
        print(f"[{index}/{len(recipients)}] Sending to {phone_number} ...")
        try:
            whatkit.sendwhatmsg_instantly(
                phone_no=phone_number,
                message=message,
                wait_time=per_send_wait_seconds,
                tab_close=tab_close,
                close_time=close_time_seconds,
            )
            # Allow WhatsApp Web to fully load, send, and settle before next recipient
            time.sleep(max(20, per_send_wait_seconds + 10))
        except Exception as error:  # noqa: BLE001
            print(f"Failed to send to {phone_number}: {error}", file=sys.stderr)
            # Small delay before proceeding to next number to avoid rapid retries
            time.sleep(5)
    print("Done.")


def normalize_number(raw_number: str, country: str = "Turkey") -> str | None:
    """Normalize phone numbers to E.164 format based on country.

    Args:
        raw_number: Raw phone number string in various formats.
        country: Country name for normalization rules.

    Returns:
        Normalized phone number in E.164 format, or None if invalid.

    Note:
        Strips spaces, dashes, parentheses.
        If already starts with '+', returns the cleaned number if valid.
    """
    if not raw_number or country not in COUNTRY_CODES:
        return None
    
    country_data = COUNTRY_CODES[country]
    country_code = country_data["code"]
    patterns = country_data["patterns"]
    
    cleaned = (
        raw_number.strip()
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )
    
    # If already in E.164 format, validate and return
    if cleaned.startswith('+'):
        return cleaned if cleaned.replace('+', '').isdigit() else None
    
    # If not all digits, skip
    if not cleaned.isdigit():
        return None
    
    # Check each pattern for the country
    for pattern in patterns:
        if cleaned.startswith(pattern):
            if pattern == country_code.replace('+', ''):
                # Full country code without +
                return "+" + cleaned
            else:
                # Local format - replace pattern with country code
                remaining = cleaned[len(pattern):]
                return country_code + remaining
    
    return None


def normalize_tr_number(raw_number: str) -> str | None:
    """Legacy function for Turkish number normalization.
    
    Maintained for backward compatibility.
    """
    return normalize_number(raw_number, "Turkey")


def send_messages_single_tab(
    recipients: list[str],
    message: str,
    initial_wait_seconds: int,
    user_data_dir_path: str | None = None,
) -> None:
    """Send messages in a single browser tab using Selenium.

    Args:
        recipients: List of phone numbers in E.164 format.
        message: Message text to send.
        initial_wait_seconds: Seconds to wait for WhatsApp Web to load initially.
        user_data_dir_path: Optional custom Chrome user data directory path.

    Raises:
        RuntimeError: If Selenium or webdriver-manager is not available.

    Note:
        - Opens WhatsApp Web once and keeps the same tab.
        - Requires the user to scan the QR on first run.
        - Navigates to each recipient's chat and sends the message.
    """
    if not SELENIUM_AVAILABLE:
        raise RuntimeError("Selenium is not available. Install with: python -m pip install selenium")

    if not recipients:
        print("No valid recipients found.")
        return

    # Prepare Chrome options to reuse a persistent (non-default) profile if provided
    chrome_options = webdriver.ChromeOptions()
    if user_data_dir_path:
        try:
            custom_dir = Path(user_data_dir_path)
            custom_dir.mkdir(parents=True, exist_ok=True)
            chrome_options.add_argument(f"--user-data-dir={str(custom_dir)}")
        except Exception:
            # Fall back silently to default behavior if parsing fails
            pass
    chrome_options.add_argument("--disable-notifications")

    if not WEBDRIVER_MANAGER_AVAILABLE:
        raise RuntimeError(
            "webdriver-manager is not available. Install with: python -m pip install webdriver-manager"
        )
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    driver.maximize_window()
    driver.get("https://web.whatsapp.com/")

    wait = WebDriverWait(driver, max(30, initial_wait_seconds))
    # Wait until chat sidebar/search becomes available (logged in)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='textbox']")))

    print(f"Starting to send message to {len(recipients)} recipient(s) in single-tab mode...")
    for index, phone_number in enumerate(recipients, start=1):
        digits_only = phone_number.replace("+", "")
        url = f"https://web.whatsapp.com/send?phone={digits_only}&text={quote_plus(message)}"
        print(f"[{index}/{len(recipients)}] Sending to {phone_number} ...")
        try:
            driver.get(url)
            # Wait until the message box for this chat is ready
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='10']")))
            # Focus message box and send ENTER to send the prefilled text
            message_box = driver.find_element(By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='10']")
            message_box.send_keys(Keys.ENTER)
            # Small settle delay between recipients
            time.sleep(3)
        except Exception as error:  # noqa: BLE001
            print(f"Failed to send to {phone_number}: {error}", file=sys.stderr)
            time.sleep(2)

    print("Done.")
    # Keep the tab open for user inspection; user can close manually


def launch_gui() -> None:
    """Launch the graphical user interface for WPBot.
    
    Creates a tkinter GUI with the following features:
    - Recipients file selection and preview
    - Number normalization for Turkish numbers
    - Message input (text area)
    - Configuration options (wait times, tab behavior)
    - Single-tab mode toggle
    - Real-time logging
    """
    root = tk.Tk()
    root.title("WPBot - WhatsApp Bulk Sender")
    root.geometry("720x540")

    main_frame = ttk.Frame(root, padding=12)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Recipients file
    recipients_label = ttk.Label(main_frame, text="Recipients .txt")
    recipients_label.grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
    recipients_var = tk.StringVar()
    recipients_entry = ttk.Entry(main_frame, textvariable=recipients_var, width=60)
    recipients_entry.grid(row=0, column=1, sticky=tk.EW, padx=4, pady=4)

    def browse_recipients() -> None:
        file_path = filedialog.askopenfilename(
            title="Select recipients .txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if file_path:
            recipients_var.set(file_path)

    browse_btn = ttk.Button(main_frame, text="Browse…", command=browse_recipients)
    browse_btn.grid(row=0, column=2, sticky=tk.W, padx=4, pady=4)

    # Country selection for normalization
    country_label = ttk.Label(main_frame, text="Country for Normalization")
    country_label.grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
    
    country_var = tk.StringVar(value="Turkey")
    country_combo = ttk.Combobox(main_frame, textvariable=country_var, width=20, state="readonly")
    country_combo['values'] = sorted(COUNTRY_CODES.keys())
    country_combo.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)
    
    # Country description
    country_desc_var = tk.StringVar(value=COUNTRY_CODES["Turkey"]["description"])
    country_desc_label = ttk.Label(main_frame, textvariable=country_desc_var, font=("TkDefaultFont", 8))
    country_desc_label.grid(row=1, column=2, sticky=tk.W, padx=4, pady=4)
    
    def update_country_desc(*args):
        selected_country = country_var.get()
        if selected_country in COUNTRY_CODES:
            country_desc_var.set(COUNTRY_CODES[selected_country]["description"])
    
    country_var.trace('w', update_country_desc)

    # Recipients preview
    recipients_preview_label = ttk.Label(main_frame, text="Recipients Preview")
    recipients_preview_label.grid(row=2, column=0, sticky=tk.NW, padx=4, pady=(8, 4))
    recipients_preview = tk.Text(main_frame, height=8, wrap=tk.NONE, state=tk.DISABLED)
    recipients_preview.grid(row=2, column=1, columnspan=2, sticky=tk.NSEW, padx=4, pady=(8, 4))

    def load_recipients_preview(file_path_str: str) -> None:
        try:
            # Load raw lines to allow normalization of local formats
            raw_lines: list[str] = []
            with Path(file_path_str).open('r', encoding='utf-8') as fh:
                raw_lines = [ln.strip() for ln in fh.readlines() if ln.strip() and not ln.lstrip().startswith('#')]
            # Show as-is first; normalization button may adjust
            numbers = raw_lines
            recipients_preview.configure(state=tk.NORMAL)
            recipients_preview.delete("1.0", tk.END)
            if numbers:
                recipients_preview.insert(tk.END, "\n".join(numbers))
            else:
                recipients_preview.insert(tk.END, "(No valid recipients found)")
            recipients_preview.configure(state=tk.DISABLED)
        except Exception as error:  # noqa: BLE001
            messagebox.showerror("WPBot", f"Failed to read recipients: {error}")

    def normalize_preview_numbers() -> None:
        # Source: current preview content if non-empty, else try file path
        recipients_preview.configure(state=tk.NORMAL)
        current_text = recipients_preview.get("1.0", tk.END).strip()
        recipients_preview.configure(state=tk.DISABLED)

        lines: list[str]
        if current_text and not current_text.startswith("(No valid"):
            lines = [ln.strip() for ln in current_text.splitlines() if ln.strip()]
        elif recipients_var.get().strip():
            try:
                with Path(recipients_var.get().strip()).open('r', encoding='utf-8') as fh:
                    lines = [ln.strip() for ln in fh.readlines() if ln.strip() and not ln.lstrip().startswith('#')]
            except Exception as error:  # noqa: BLE001
                messagebox.showerror("WPBot", f"Failed to read recipients: {error}")
                return
        else:
            messagebox.showinfo("WPBot", "Please select a recipients file or paste numbers into the preview.")
            return

        normalized: list[str] = []
        selected_country = country_var.get()
        for ln in lines:
            result = normalize_number(ln, selected_country)
            if result:
                normalized.append(result)

        # De-duplicate while preserving order
        seen: set[str] = set()
        unique_normalized = []
        for num in normalized:
            if num not in seen:
                seen.add(num)
                unique_normalized.append(num)

        recipients_preview.configure(state=tk.NORMAL)
        recipients_preview.delete("1.0", tk.END)
        if unique_normalized:
            recipients_preview.insert(tk.END, "\n".join(unique_normalized))
        else:
            recipients_preview.insert(tk.END, "(No numbers matched normalization rules)")
        recipients_preview.configure(state=tk.DISABLED)

    # After defining preview loader, update browse to fill it
    def browse_recipients() -> None:
        file_path = filedialog.askopenfilename(
            title="Select recipients .txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if file_path:
            recipients_var.set(file_path)
            load_recipients_preview(file_path)

    # Message
    message_label = ttk.Label(main_frame, text="Message")
    message_label.grid(row=3, column=0, sticky=tk.NW, padx=4, pady=(8, 4))
    message_text = tk.Text(main_frame, height=8, wrap=tk.WORD)
    message_text.grid(row=3, column=1, columnspan=2, sticky=tk.NSEW, padx=4, pady=(8, 4))

    # Options frame
    options_frame = ttk.LabelFrame(main_frame, text="Options", padding=8)
    options_frame.grid(row=4, column=0, columnspan=3, sticky=tk.EW, padx=4, pady=8)

    wait_label = ttk.Label(options_frame, text="Wait (seconds)")
    wait_label.grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
    wait_var = tk.IntVar(value=40)
    wait_spin = ttk.Spinbox(options_frame, from_=1, to=120, textvariable=wait_var, width=6)
    wait_spin.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)

    close_label = ttk.Label(options_frame, text="Close time (seconds)")
    close_label.grid(row=0, column=2, sticky=tk.W, padx=12, pady=4)
    close_var = tk.IntVar(value=3)
    close_spin = ttk.Spinbox(options_frame, from_=1, to=60, textvariable=close_var, width=6)
    close_spin.grid(row=0, column=3, sticky=tk.W, padx=4, pady=4)

    keep_tab_var = tk.BooleanVar(value=True)
    single_tab_var = tk.BooleanVar(value=False)
    keep_tab_check = ttk.Checkbutton(options_frame, text="Keep tab open", variable=keep_tab_var)
    keep_tab_check.grid(row=0, column=4, sticky=tk.W, padx=12, pady=4)
    single_tab_check = ttk.Checkbutton(options_frame, text="Single-tab mode (Selenium)", variable=single_tab_var)
    single_tab_check.grid(row=0, column=5, sticky=tk.W, padx=12, pady=4)

    # Log area
    log_label = ttk.Label(main_frame, text="Log")
    log_label.grid(row=5, column=0, sticky=tk.NW, padx=4, pady=(8, 4))
    log_text = tk.Text(main_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
    log_text.grid(row=5, column=1, columnspan=2, sticky=tk.NSEW, padx=4, pady=(8, 4))

    def append_log(line: str) -> None:
        log_text.configure(state=tk.NORMAL)
        log_text.insert(tk.END, line + "\n")
        log_text.see(tk.END)
        log_text.configure(state=tk.DISABLED)

    def on_send() -> None:
        recipients_path_str = recipients_var.get().strip()
        message_value = message_text.get("1.0", tk.END).strip()
        if not message_value:
            messagebox.showerror("WPBot", "Please enter a message to send.")
            return

        wait_seconds = int(wait_var.get())
        close_seconds = int(close_var.get())
        tab_close = not keep_tab_var.get()

        send_btn.configure(state=tk.DISABLED)
        append_log("Reading recipients and starting to send...")

        def worker() -> None:
            try:
                # Prefer numbers from preview if present, else read from file
                recipients_preview.configure(state=tk.NORMAL)
                preview_text = recipients_preview.get("1.0", tk.END).strip()
                recipients_preview.configure(state=tk.DISABLED)

                if preview_text and not preview_text.startswith("("):
                    recipients_list: list[str] = []
                    for ln in preview_text.splitlines():
                        val = ln.strip()
                        if val and val.startswith('+') and val.replace('+', '').isdigit():
                            recipients_list.append(val)
                else:
                    if not recipients_path_str:
                        raise ValueError("Please select a recipients .txt file or normalize/paste numbers in the preview.")
                    recipients_list = read_recipients_from_file(Path(recipients_path_str))
                if not recipients_list:
                    root.after(0, lambda: append_log("No valid recipients found in file."))
                    return
                # Use single-tab mode if selected and available
                if single_tab_var.get():
                    if not SELENIUM_AVAILABLE:
                        raise RuntimeError("Selenium not installed. Install with: python -m pip install selenium")
                    send_messages_single_tab(
                        recipients=recipients_list,
                        message=message_value,
                        initial_wait_seconds=wait_seconds,
                        user_data_dir_path=None,  # Use default Chrome profile
                    )
                else:
                    # Use existing pywhatkit path
                    send_messages_to_recipients(
                        recipients=recipients_list,
                        message=message_value,
                        per_send_wait_seconds=wait_seconds,
                        tab_close=tab_close,
                        close_time_seconds=close_seconds,
                    )
                root.after(0, lambda: append_log("Finished sending."))
            except FileNotFoundError as fnf_error:
                root.after(0, lambda e=fnf_error: messagebox.showerror("WPBot", str(e)))
            except Exception as error:  # noqa: BLE001
                root.after(0, lambda e=error: messagebox.showerror("WPBot", f"Error: {e}"))
            finally:
                root.after(0, lambda: send_btn.configure(state=tk.NORMAL))

        threading.Thread(target=worker, daemon=True).start()

    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=6, column=0, columnspan=3, sticky=tk.EW, padx=4, pady=8)
    normalize_btn = ttk.Button(button_frame, text="Normalize Numbers", command=normalize_preview_numbers)
    normalize_btn.pack(side=tk.LEFT, padx=4)
    send_btn = ttk.Button(button_frame, text="Send", command=on_send)
    send_btn.pack(side=tk.RIGHT, padx=4)
    quit_btn = ttk.Button(button_frame, text="Quit", command=root.destroy)
    quit_btn.pack(side=tk.RIGHT, padx=4)

    # Grid weights
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(2, weight=1)
    main_frame.rowconfigure(3, weight=1)
    main_frame.rowconfigure(5, weight=1)

    root.mainloop()

def build_arg_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser.
    
    Returns:
        Configured ArgumentParser with all WPBot command-line options.
    """
    parser = argparse.ArgumentParser(description="Send a WhatsApp message to many recipients from a text file.")
    parser.add_argument(
        "--recipients",
        help="Path to a .txt file with one phone number per line (in E.164 format, e.g., +1234567890). Required unless --gui.",
    )
    parser.add_argument(
        "--message",
        help="Message text to send. Use --message-file to read from a file instead.",
    )
    parser.add_argument(
        "--message-file",
        help="Path to a text file whose entire contents will be sent as the message.",
    )
    parser.add_argument(
        "--wait",
        type=int,
        default=40,
        help="Seconds to wait for WhatsApp Web to load before sending (default: 40).",
    )
    parser.add_argument(
        "--close-time",
        type=int,
        default=3,
        help="Seconds to wait before closing the tab after sending (default: 3).",
    )
    parser.add_argument(
        "--keep-tab-open",
        action="store_true",
        help="Do not auto-close the WhatsApp tab after sending.",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch a simple GUI to select recipients file and enter a message.",
    )
    return parser


def main() -> None:
    """Main entry point for WPBot.
    
    Launches GUI by default if no arguments provided, otherwise processes command-line arguments.
    """
    # If launched without any arguments (e.g., double-click on Windows), open the GUI by default
    if len(sys.argv) == 1:
        launch_gui()
        return

    parser = build_arg_parser()
    args = parser.parse_args()

    if getattr(args, "gui", False):
        launch_gui()
        return

    if not args.recipients:
        parser.error("--recipients is required when not using --gui")

    recipients_path = Path(args.recipients)
    recipients = read_recipients_from_file(recipients_path)

    message_file_path = Path(args.message_file) if args.message_file else None
    message = read_message(args.message, message_file_path)

    send_messages_to_recipients(
        recipients=recipients,
        message=message,
        per_send_wait_seconds=args.wait,
        tab_close=not args.keep_tab_open,
        close_time_seconds=args.close_time,
    )


if __name__ == "__main__":
    main()


