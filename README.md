# Freshbooks APIs in Django
An integration of Freshbooks APIs in a Django e-commerce web app.

## How to run

### Set up  virtual environment
```
python3 -m venv venv
source venv/bin/activate
```

### Install the dependencies

```
pip install -r requirements.txt
```

### Build the project

```
python3 manage.py makemigrations
python3 manage.py migrate
```

### Run the project

```
python3 manage.py runserver
```

## Data update

If you want to update the data, open the admin portal (`/admin`) and use the following credentials to log in:

**Username:** educative\
**Password:** edu123
