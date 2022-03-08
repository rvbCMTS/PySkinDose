@ECHO OFF
cd %~dp0
cd docs
sphinx-apidoc -o source ../src/pyskindose
make clean && make html && cd ..
