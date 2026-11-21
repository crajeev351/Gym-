# IronForge Fitness client demo

Extract the ZIP and open this folder in VS Code. Python 3.10 or later is required. Install the dependencies before the meeting.

**macOS or Linux**

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python demo.py
```

**Windows PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe demo.py
```

Open [the public site](http://127.0.0.1:5000/) and [the staff portal](http://127.0.0.1:5000/admin/login) in two tabs. The first run prints the generated password for the `demo` account. Keep it for future runs. Leave the terminal running during the presentation. If port 5000 is busy, add `--port 5050` and use 5050 in the URLs.

## Three-minute walkthrough

1. Open the landing page. Select **Muscle Gain**, then **Couples Training**. Show how both choices carry into the trial form.
2. Submit a trial request using sample details, such as **Demo Visitor**, **9000000000** and **visitor@example.test**. The confirmation tells the visitor what to expect next.
3. Open the staff dashboard. Find the new request under **Leads**, move it to **Contacted**, and demonstrate filtering and CSV export.
4. Open **Site Settings & SEO** to show where staff can update business details, contact links and branding.

The demo uses `instance/gym_demo.db`, a separate SQLite database initialized with eight fictional leads. Changes in the demo carry over between runs. Business details and headline statistics come from the repository's sample content. Replace them with client-approved values before publishing.
