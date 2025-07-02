Install Poppler for Windows
🔧 Step-by-step:
Download Poppler (Windows binaries):
https://github.com/oschwartz10612/poppler-windows/releases/

📦 Choose latest poppler-xx_xx_xx-xxx.zip

Extract it
Extract to:
C:\Program Files\poppler-xx\
(e.g., C:\Program Files\poppler-24.07.0\)

Add Poppler to System PATH

Press Win + S, type "environment variables"

Click Environment Variables

Under System variables, select Path → click Edit

Click New → paste this:

makefile
Copy
Edit
C:\Program Files\poppler-24.07.0\Library\bin
Click OK → OK → OK

✅ Restart your terminal/VSCode

Re-run:

bash
Copy
Edit
python chunk_and_embed.py