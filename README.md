# 🤖 System AI Assistant

A powerful, voice-enabled, and extensible desktop assistant developed by Mohd Eisa. This assistant uses the Gemini API with Function Calling to execute system commands, manage files, open applications, and automate web messaging (WhatsApp/Telegram).

## ✨ Features

* **System Automation:** Create files/directories, execute shell commands, and manage system executables.
* **API Key Failover:** Supports up to **4 Gemini API keys** for automatic rotation and fallback in case of rate limiting or overload errors (503 UNAVAILABLE).
* **Voice Toggle:** Starts in Keyboard (text) mode and can be switched to fully Voice-Controlled mode using the command `enable voice assistant`.
* **Web Messaging:** Automates sending messages via WhatsApp Web or Telegram Web using **Selenium** and pre-configured browser profiles.
* **Multilingual:** Understands Hindi and English, and replies in Hinglish (Hindi typed in English) as per the system instruction.

***

## 🚀 Setup & Installation

### 1. Clone the Repository

```bash
git clone [https://github.com/eisaalsa555/SystemAi_Assistant.git](https://github.com/eisaalsa555/SystemAi_Assistant.git)
cd SystemAi_Assistant
```
### 2. Create and Activate Virtual Environment
## It is highly recommended to use a virtual environment.

# Create environment
```python
python -m venv venv
```
# Activate environment (Windows)
```powershell
.\venv\Scripts\activate
```
# Activate environment (Linux/macOS)
```
source venv/bin/activate
```
###3. Install Dependencies
##The project requires several Python libraries, including google-genai and selenium for web automation.
```python pip
pip install -r requirements.txt
```
###🔑 Configuration Files Setup
###4. API Key Configuration
##Copy the example environment file and fill in your Gemini API keys. The assistant will try keys 1 through 4 sequentially.
# Note: Ensure you have the Chrome browser installed for Selenium to work.
##copy .env.sample .env

# .env
```env
GEMINI_API_KEY_1="YOUR_GEMINI_API_KEY"
GEMINI_API_KEY_1="YOUR_FIRST_GEMINI_API_KEY"
GEMINI_API_KEY_2="YOUR_SECOND_GEMINI_KEY"
GEMINI_API_KEY_3="YOUR_THIRD_GEMINI_KEY"
GEMINI_API_KEY_4="YOUR_FOURTH_GEMINI_KEY"
```
###5. Web Messaging Configuration (Crucial Step)
##The send_web_message tool requires configuration files that tell Selenium where your logged-in browser profile is.

##Find Chrome User Data Path: Open Chrome, go to chrome://version, and copy the Profile Path. You need the root User Data path (e.g., C:\Users\Mohd Eisa\AppData\Local\Google\Chrome\User Data). Remove the specific profile folder like \Default or \Profile 1.

##Create Config Files: Create the following two JSON files in your project root directory and update the browser_profile_path value:
##whatsapp_config.json
```json
{
    "url": "[https://web.whatsapp.com/](https://web.whatsapp.com/)",
    "status": "logged_in",
    "browser_profile_path": "C:\\Users\\Your_User\\AppData\\Local\\Google\\Chrome\\User Data"
}
```
##telegram_config.json
```json
{
    "url": "[https://web.telegram.org/a/](https://web.telegram.org/a/)",
    "status": "logged_in",
    "browser_profile_path": "C:\\Users\\Your_User\\AppData\\Local\\Google\\Chrome\\User Data"
}
```
####⚠️ IMPORTANT: When using the web messaging feature, ensure that no Chrome window using the configured profile is open, otherwise the automation will crash due to file lock issues.
###▶️ How to Run & Use
## WARNING ⚠️: Before Run Ensure You Succesfully Installed All Libaries & Activate Your Environment
#Manual Start
```Bash
python main.py
```
| Command / Input                               | Mode             | Description                           |
| --------------------------------------------- | ---------------- | ------------------------------------- |
| `python main.py`                              | Keyboard Mode    | Starts the assistant                  |
| `enable voice assistant`                      | Keyboard → Voice | Enables microphone mode               |
| `deactivate voice`                            | Voice → Keyboard | Switches back to text mode            |
| `whatsapp par Bhaskar ko message karo ki ...` | Both             | Sends WhatsApp message using Selenium |
| `File ka naam new_file.txt se banao`          | Both             | Creates a new file                    |
| `exit`                                        | Both             | Shuts down the assistant              |





👤 Author

Mohd Eisa
Full Stack Developer & Ethical Hacker

🔗 Portfolio: https://eisa.lovable.app

🔗 GitHub: https://github.com/eisaalsa555

⭐ If you like this project, don't forget to star the repository!
