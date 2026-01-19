import hexchat
import subprocess
import re

# Define pattern for the specific quit reason
# This matches the "*.net *.split" phrase commonly seen during server splits
QUIT_REASON_PATTERN = re.compile(
    r'.*\.net \*\.split',
    re.IGNORECASE
)

# Pushover alerting module
__module_name__ = 'pushover'
__module_version__ = '0.5'
__module_description__ = 'Alerts on mentions and specific Gatekeeper quits'

PUSHOVER_APP_TOKEN = '#enter your token here'
PUSHOVER_USER_TOKEN = '#enter your token here'

# --- HELPER FUNCTIONS ---

def send_pushover_message(message):
    """Sends an alert message to Pushover."""
    # Using a list for Popen is safer and prevents shell parsing errors 
    # with special characters (like '&' or '?') found in IRC links.
    curl_cmd = [
        'curl', '-s',
        '--form-string', f'token={PUSHOVER_APP_TOKEN}',
        '--form-string', f'user={PUSHOVER_USER_TOKEN}',
        '--form-string', f'message={message}',
        '--form-string', 'sound=echo',
        '--form-string', 'priority=2',
        '--form-string', 'retry=60',
        '--form-string', 'expire=1800',
        'https://api.pushover.net/1/messages.json'
    ]
    subprocess.Popen(curl_cmd)

def callback_mention_or_pm(word, wordeol, userdata):
    """Triggers when your nick is highlighted or you get a PM."""
    channel = hexchat.get_info('channel')
    nick = word[0]
    msg_content = word[1]
    
    # Label private messages clearly
    if channel == nick:
        channel = 'Private'
        
    alert_text = f'{channel} - {nick}: {msg_content}'
    send_pushover_message(alert_text)
    return hexchat.EAT_NONE

def callback_quit_pattern(word, wordeol, userdata):
    """Triggers on user quit events, filtered for Gatekeeper splits."""
    nick = word[0]
    reason = word[1]

    # Only alert if the nick is Gatekeeper AND it matches the split pattern
    if nick == "Gatekeeper" and QUIT_REASON_PATTERN.search(reason):
        message = f'[QUIT MATCH] {nick} has quit ({reason})'
        send_pushover_message(message)

    return hexchat.EAT_NONE

# --- HOOKS ---

# 1. Alert on Mentions (Highlights) and Private Messages
# These hooks only fire if someone mentions your nick or PMs you directly.
hexchat.hook_print("Channel Msg Hilight", callback_mention_or_pm)
hexchat.hook_print("Channel Action Hilight", callback_mention_or_pm)
hexchat.hook_print("Private Message to Dialog", callback_mention_or_pm)
hexchat.hook_print("Private Action to Dialog", callback_mention_or_pm)

# 2. Alert on Gatekeeper quitting with a split reason
hexchat.hook_print("Quit", callback_quit_pattern)


hexchat.prnt('Pushover alert plugin (v0.5) loaded: Monitoring mentions and Gatekeeper.')

