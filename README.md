# Asterisk Voice Control

This is a proof of concept for basic control of Asterisk calls with voice commands, using Asterisk' EAGI protocol and Picovoice.

It demonstrates dialing an extension when a caller says "hey asterisk dial X".

[Picovoice.ai](https://picovoice.ai/) voice recognition is trained offline but runs on-premise for privacy, performance, and reliability.

## Limitations

* Only extensions can be dialed, not outside lines
* Only 1 person can be bridged into the call, not multiple
* It can’t do anything else after bridging in someone
* It's not easy to say "asterisk" (but that's trivially changed)
* Probably a lot more than those 4 things...

Did I mention this is a proof of concept?

## Setup

To run this yourself, follow these steps. These were written using a Digital Ocean droplet provisioned from [this FreePBX marketplace app](https://marketplace.digitalocean.com/apps/freepbx-1).

1. Install Asterisk and FreePBX. FreePBX is optional but makes setup easier.
1. Visit the FreePBX web app (https://{your droplet IP}). Configure:
   1. Change chan_pjsip to port 5160 and chan_sip to 5060 for best compatibility (Settings > Asterisk SIP settings)
   1. Optional- whitelist your IP address so Fail2Ban doesn't lock you out.
1. Configure 3 extensions as follows (Applications > Extensions > Quick create extension)
   1. Single-digit extensions
   1. Good passwords
1. Install softphones on desktop and/or mobile. Linphone is decent. Configure the accounts and test calls between the extensions.
1. Ensure python3 and pip are installed on the server.
1. Copy the .py, .rhn, and .ppn files to /var/lib/asterisk/agi-bin/ and set permissions and ownership. Each should be owned by asterisk:asterisk, and the `picovoice-dial.py` file should be executable.
1. Install Python libraries mentioned in `requirements.txt`
1. Sign up for a [free Picovoice.ai account](https://console.picovoice.ai/).
1. Make a file `/var/lib/asterisk/agi-bin/picovoice.key` with your picovoice API key, and chmod 600 and set ownership to asterisk:asterisk.
1. Copy the `extensions_custom.conf` example file to `/etc/asterisk/extensions_custom.conf`
1. Reload the dialplan (`dialplan reload` on the CLI)
1. From a phone, dial extension 4, then after the "weasels have eaten our phone system" greeting, say "hey asterisk dial 1" (or 2, or 3). the extension is dialed and if picked up, it is bridged into the call.

## Licence

Copyright 2023 Matthew Fox

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
