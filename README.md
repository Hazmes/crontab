# crontab

2 functions that will take a cron string and parse it.

They return a dictionary with a list for each of the cron expression.

This allows you to compare the current date against the returned dictionary.

These functions rely on the `re` module and have no other dependencies outside the standard library

Some pytests are provided. You can run them with `pytest -vv crontab.py`
