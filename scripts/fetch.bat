@echo off

pushd "%~dp0\.."
call .venv\Scripts\activate
python -m src.fetch %*
popd
