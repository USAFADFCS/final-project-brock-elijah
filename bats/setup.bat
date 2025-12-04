python -m venv ./env

call enter.bat
python -m pip install requests
python -m pip install openai
python -m pip install flask
python -m pip install beautifulsoup4
python -m pip install pypdf
python -m pip install playwright
python -m playwright install chromium

echo SETUP COMPLETE
pause