# To start develop run:
```shell
python -m venv venv
```
(On Windows):
```shell
venv\Scripts\activate
```
(On MacOS):
```shell
source venv/bin/activate
```
### After that click in bottom right corner on Python -> Add New Interpreter -> Add Local -> Existing -> Okay
### After you may continue:
```shell
pip install -r requirements.txt
```
## To start testing run:
```shell
pytest && flake8
```