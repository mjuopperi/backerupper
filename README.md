# backerupper

1. Install dependencies: `pipenv install`

2. Change settings in [backup.py](backup.py)

3. Set up a backup schedule 

    For mac:
   - Change settings in [launched.backup.plist](launched.backup.plist)
   - Copy it to  ~/Library/LaunchAgents
   - Load it `launchctl load -w ~/Library/LaunchAgents/launched.backup.plist`
