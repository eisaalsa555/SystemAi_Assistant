import os
import subprocess
import webbrowser
import platform
import json
from glob import glob
from typing import List, Optional
# tools.py (Add this function)

from selenium import webdriver #type: ignore
from selenium.webdriver.chrome.service import Service #type: ignore
from selenium.webdriver.common.by import By #type: ignore
from selenium.webdriver.support.ui import WebDriverWait #type: ignore
from selenium.webdriver.support import expected_conditions as EC #type: ignore
import time 

# --- CONFIGURATION (Ensure these paths are created in your project folder) ---
WHATSAPP_CONFIG_FILE = "whatsapp_config.json"
TELEGRAM_CONFIG_FILE = "telegram_config.json"

def load_web_config(app_name: str) -> dict:
    """Loads configuration for a specific web application."""
    if app_name.lower() == 'whatsapp':
        file_path = WHATSAPP_CONFIG_FILE
    elif app_name.lower() == 'telegram':
        file_path = TELEGRAM_CONFIG_FILE
    else:
        return {}
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}

def send_web_message(app_name: str, contact_name: str, message_content: str) -> str:
    """
    Automates sending a message via WhatsApp Web or Telegram Web using Selenium.
    
    Note: Requires a pre-configured browser profile for login persistence.
    """
    app_name = app_name.lower()
    config = load_web_config(app_name)
    
    if not config or not config.get('browser_profile_path'):
        return f"ERROR: Configuration for {app_name} not found or profile path missing. Please create {app_name}_config.json."

    # --- Selenium Setup ---
    try:
        chrome_options = webdriver.ChromeOptions()
        # Essential step: Load the pre-logged-in browser profile
        chrome_options.add_argument(f"user-data-dir={config['browser_profile_path']}")
        chrome_options.add_argument("--headless")  # Run in background without showing UI
        
        # Initialize the WebDriver
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(config['url'])
        
        wait = WebDriverWait(driver, 30) # Wait up to 30 seconds for elements

    except Exception as e:
        return f"ERROR: Could not initialize Selenium/Browser. Driver/Profile error: {e}"

    # --- Messaging Logic (HIGHLY simplified - This part is complex and needs precise locators) ---
    try:
        if app_name == 'whatsapp':
            # 1. Wait for WhatsApp to load (search bar presence)
            search_box = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')))
            search_box.send_keys(contact_name)
            time.sleep(2) 
            
            # 2. Click the contact (Locator is complex and changes often)
            contact = wait.until(EC.presence_of_element_located((By.XPATH, f'//span[@title="{contact_name}"]')))
            contact.click()
            
            # 3. Type message (Locator is complex and changes often)
            message_area = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))) 
            message_area.send_keys(message_content)
            
            # 4. Click send (Locator is complex and changes often)
            send_button = wait.until(EC.presence_of_element_located((By.XPATH, '//span[@data-icon="send"]')))
            send_button.click()
            
            result = f"SUCCESS: Message sent to {contact_name} on {app_name}."

        elif app_name == 'telegram':
            # Telegram logic here (uses different XPATHs/CSS Selectors)
            result = f"INFO: Telegram automation logic needs to be fully implemented."
            
        else:
            result = "ERROR: Unsupported web application for messaging."

    except Exception as e:
        result = f"ERROR during automation ({app_name}): Failed to find contact or send message. Reason: {e}"

    finally:
        driver.quit() # Always close the browser instance
        return result

# --- External Libraries ---
try:
    import phonenumbers #type: ignore
    from phonenumbers import geocoder, carrier, timezone #type: ignore
    PHONENUMBERS_AVAILABLE = True
except ImportError:
    PHONENUMBERS_AVAILABLE = False


# --- File Management Tools ---

def create_file(filename: str, content: Optional[str] = "") -> str:
    """Creates a new file and optionally writes content to it. Returns success/error message."""
    try:
        with open(filename, 'w') as f:
            f.write(content)
        return f"SUCCESS: File '{filename}' created and content written."
    except Exception as e:
        return f"ERROR: Could not create file '{filename}'. Reason: {e}"

def create_directory(dirname: str) -> str:
    """Creates a new directory (folder). Returns success/error message."""
    try:
        os.makedirs(dirname, exist_ok=True)
        return f"SUCCESS: Directory '{dirname}' created successfully."
    except Exception as e:
        return f"ERROR: Could not create directory '{dirname}'. Reason: {e}"

def list_current_directory_contents() -> str:
    """Lists all files and directories in the current working directory."""
    try:
        items = os.listdir('.')
        return "SUCCESS: Current directory contents: " + ", ".join(items)
    except Exception as e:
        return f"ERROR: Could not list directory contents. Reason: {e}"

# --- System Execution Tools ---

def execute_command(command: str, args: Optional[List[str]] = None) -> str:
    """
    Executes a system command (e.g., 'git status', 'python script.py', 'code .').
    Returns the command's output or an error message.
    """
    full_command = [command] + (args if args else [])
    try:
        result = subprocess.run(
            full_command, 
            capture_output=True, 
            text=True, 
            check=True, 
            shell=True 
        )
        output_report = f"COMMAND OUTPUT:\n{result.stdout}\nCOMMAND ERROR (if any):\n{result.stderr}"
        return output_report
    except subprocess.CalledProcessError as e:
        return f"ERROR: Command failed with exit code {e.returncode}. Stderr: {e.stderr}"
    except FileNotFoundError:
        return f"ERROR: Command '{command}' not found on the system path."
    except Exception as e:
        return f"ERROR: An unexpected error occurred while running command: {e}"


def open_application_or_url(target_type: str, target_name: str, search_query: Optional[str] = None) -> str:
    """
    Opens a system application or a specific URL/search query in the default web browser.
    """
    target_type = target_type.lower()
    
    if target_type == 'app':
        try:
            subprocess.Popen([target_name], shell=True)
            return f"SUCCESS: Attempted to open application '{target_name}'. Please check your screen."
        except Exception as e:
            return f"ERROR: Could not open application '{target_name}'. Reason: {e}"

    elif target_type == 'site':
        search_templates = {
            'youtube': "https://www.youtube.com/results?search_query=",
            'google': "https://www.google.com/search?q=",
            'spotify': "https://open.spotify.com/search/",
            'whatsapp': "https://web.whatsapp.com/",
            'telegram': "https://web.telegram.org/k/",
            'portfolio': "https://mohd-eisa.lovable.app",
            'alsa-ai': "https://alsa-ai.lovable.app",
            'github': "https://github.com",
            'stackoverflow': "https://stackoverflow.com/search?q=",
        }
        
        if target_name.lower() in search_templates:
            base_url = search_templates[target_name.lower()]
            if search_query:
                full_url = base_url + search_query.replace(" ", "+")
                webbrowser.open_new_tab(full_url)
                return f"SUCCESS: Opened {target_name} with search query: '{search_query}'."
            else:
                webbrowser.open_new_tab(target_name.lower())
                return f"SUCCESS: Opened the main page of {target_name}."

        elif target_name.startswith('http') or '.' in target_name:
            url_to_open = target_name if target_name.startswith(('http://', 'https://')) else 'https://' + target_name
            if search_query:
                full_url = "https://www.google.com/search?q=" + (url_to_open + " " + search_query).replace(" ", "+")
                webbrowser.open_new_tab(full_url)
                return f"SUCCESS: Performed Google search for: '{target_name} {search_query}'."
            else:
                webbrowser.open_new_tab(url_to_open)
                return f"SUCCESS: Opened URL: '{url_to_open}' in the browser."

        else:
            return "ERROR: Invalid site request. Please specify a known site (youtube, google, spotify) or a full URL/domain."
            
    return "ERROR: Invalid target_type specified. Use 'app' or 'site'."

# --- Phone Number Lookup Tool ---

def lookup_phone_number_info(phone_number: str) -> str:
    """
    Looks up and returns basic information about a given phone number, 
    including country, carrier, and timezone. The input MUST be in E.164 format (e.g., +919876543210).
    """
    if not PHONENUMBERS_AVAILABLE:
        return "ERROR: The 'phonenumbers' library is not installed. Please install it using 'pip install phonenumbers'."
        
    try:
        parsed_number = phonenumbers.parse(phone_number, None)
    except phonenumbers.phonenumberutil.NumberParseException:
        return "ERROR: Invalid phone number format provided. Please use the full international format (e.g., +91...)."
    
    if not phonenumbers.is_valid_number(parsed_number):
        validity = "No (Invalid number length/format)"
    else:
        validity = "Yes"

    country = geocoder.description_for_number(parsed_number, "en")
    service_provider = carrier.name_for_number(parsed_number, "en")
    time_zones = timezone.time_zones_for_number(parsed_number)

    result = (
        "\n--- Phone Lookup Results ---"
        f"\nNumber:           {phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}"
        f"\nIs Valid:         {validity}"
        f"\nRegion/Country:   {country}"
        f"\nCarrier/Provider: {service_provider if service_provider else 'N/A'}"
        f"\nTimezone(s):      {', '.join(time_zones) if time_zones else 'N/A'}"
        "\n--------------------------"
    )
    return result

# --- System Scanning Tool ---

def get_scan_directories() -> list:
    """Returns a list of common application directories based on the operating system."""
    system = platform.system()
    if system == "Windows":
        return [
            os.path.join(os.environ.get('PROGRAMFILES', ''), '*'), 
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WindowsApps', '*'),
        ]
    elif system == "Linux" or system == "Darwin": 
        return ['/usr/bin/*', '/usr/local/bin/*', '/Applications/*']
    else:
        return []

def scan_system_for_executables(output_file: str = "discovered_apps.json") -> str:
    """
    Scans common application directories for executables and saves a list 
    of their names and paths to a JSON file.
    """
    discovered_apps = {}
    
    try:
        for base_path_wildcard in get_scan_directories():
            for path in glob(base_path_wildcard):
                if os.path.isfile(path) and (os.access(path, os.X_OK) or path.endswith(('.exe', '.lnk'))):
                    app_name = os.path.basename(path)
                    app_name_clean = app_name.split('.')[0].lower()
                    
                    if app_name_clean and app_name_clean not in discovered_apps:
                        discovered_apps[app_name_clean] = path 

        with open(output_file, 'w') as f:
            json.dump(discovered_apps, f, indent=4)
            
        return f"SUCCESS: Found {len(discovered_apps)} potential applications. List saved to '{output_file}'. Relaunch assistant to load them."
        
    except Exception as e:
        return f"ERROR during system scan: {e}"


# tools.py (Add this function)
# ... (Baaki saare existing functions) ...

SHORTCUTS_FILE = "shortcuts.json"

def assign_keyboard_shortcut(app_name: str, shortcut: str) -> str:
    """
    Assigns a user-defined keyboard shortcut (e.g., 'Ctrl+Alt+C') to a discovered application.
    This saves the shortcut mapping to a dedicated JSON file.
    
    Args:
        app_name: The clean name of the application (e.g., 'chrome', 'notepad').
        shortcut: The keyboard shortcut string (e.g., 'Ctrl+Shift+E').
    
    Returns:
        A message confirming the assignment or reporting an error.
    """
    try:
        # 1. Existing shortcuts load karo
        if os.path.exists(SHORTCUTS_FILE):
            with open(SHORTCUTS_FILE, 'r') as f:
                shortcuts = json.load(f)
        else:
            shortcuts = {}

        # 2. Assignment karo
        shortcuts[app_name.lower()] = shortcut
        
        # 3. Save wapas karo
        with open(SHORTCUTS_FILE, 'w') as f:
            json.dump(shortcuts, f, indent=4)
            
        return f"SUCCESS: Shortcut '{shortcut}' assigned to application '{app_name}'. Saved to {SHORTCUTS_FILE}."
        
    except Exception as e:
        return f"ERROR assigning shortcut for '{app_name}': {e}"