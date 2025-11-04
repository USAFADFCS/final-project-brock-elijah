python -m venv ./env
call enter.bat

python -m pip install --upgrade pip
call inst_dependencies.bat


xcopy .env.example .env

move ./junk/requirements.txt ./requirements.txt
python verify_setup.py
move ./requirements.txt ./junk/requirements.txt

