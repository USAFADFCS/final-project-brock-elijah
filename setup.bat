python -m venv ./env
call enter.bat
python -m pip install -r ./junk/requirements.txt

xcopy .env.example .env

move ./junk/requirements.txt ./requirements.txt
python verify_setup.py
move ./requirements.txt ./junk/requirements.txt

