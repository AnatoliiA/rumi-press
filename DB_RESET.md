
Resetting your Database
-----------------------

If you have a problem running `migrate` or `makemigrations`, you can start over with a
clean SQLite database.

(1) Activate your virtual environment and go to your project directory (for example
`~/django_projects/market`).

(2) **Delete the database file.** From the project root (the directory that contains
`manage.py`), remove `db.sqlite3`:

    rm db.sqlite3

On Windows, delete `db.sqlite3` in File Explorer or use `del db.sqlite3` in Command Prompt.

(3) **Recreate the database** using your existing migration files:

    python manage.py migrate

(4) **Create a new admin account** (your old users were in the deleted file):

    python manage.py createsuperuser

If you changed models and need new migrations, run `python manage.py makemigrations`
before `migrate`.
