# Lab 7 Python testing

Joseph Awaida

This submission tests the Lab 5 Flask and SQLite user application using pytest. The original app.py and database.py are unchanged from https://github.com/j123awaida/Lab5-Postman-APIs. Only the graded activity is included; the capitalize, wallet, and example addition applications are not included.

## Install and test

Use Python 3.10 or later. From the Lab7-Joseph-Awaida directory:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -v
```

On Windows use `python` instead of `python3` and activate with `.venv\Scripts\activate`.

## Requirement mapping

| Lab requirement | Test |
| --- | --- |
| First app run creates the database | test_database_created_on_first_app_run |
| Insert_user | test_insert_user |
| Get_users | test_get_users |
| Get_users_by_id | test_get_user_by_id |
| Update_user | test_update_user |
| Delete_user | test_delete_user |
| Api_get_user | test_api_get_user |
| Api_add_user | test_api_add_user |
| Api_update_user | test_api_update_user |
| Api_delete_user | test_api_delete_user |

The lab's function labels correspond to the lowercase names in the original project. Get_users_by_id corresponds to get_user_by_id. Three additional tests check the users list API, missing-user lookup, and retrieval from an empty table. Total: 13 tests.

## Test isolation and assertions

Each test uses a new pytest temporary directory and database. The populated_database fixture loads known records directly with SQL, so fixture setup does not depend on insert_user working correctly. Joseph's record comes from the original Postman example; the second record is synthetic. Direct SQL reads verify persistence and ensure unrelated users survive updates and deletions. The original Lab 5 database is never modified.

The first-run test executes app.py as __main__ with Flask.run replaced by a harmless function. It checks that startup creates the database, all six table columns, and an empty users table. The supplied Lab 5 implementation does not seed users on startup. This suite preserves that previously graded behavior; known users are checked after fixture setup in the retrieval tests. No initial users are invented as application requirements.

Flask's test client exercises the real routes without a running server. Every required API test checks HTTP status, JSON content, and persisted data. Add and update requests send JSON payloads and compare every returned field; deletion checks its confirmation and the absence of the record. The original API returns 200 for success, including creation and deletion, and 200 with an empty object for an unknown user. Tests follow that existing contract.

## Submission

Submit a text file containing https://github.com/j123awaida/Lab7-Joseph-Awaida to Moodle. A project ZIP is also available as a local backup. The ZIP contains the application, tests, configuration, dependency pins, documentation, and actual pytest output under evidence/. The snapshot displays real captured pytest output in a browser results page. To capture a terminal application screenshot instead, run `python -m pytest -v` and capture the passing summary and project path.
