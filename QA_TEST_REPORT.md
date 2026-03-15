# QA Test Report — main
## Code Review
Not performed in this phase.
## Unit Test Results
Not performed in this phase.
## Live API Test Results (curl)
| # | Endpoint | Method | Payload | Expected | Actual Status | Result |
|---|----------|--------|---------|----------|---------------|--------|
| 1 | /auth/register | POST | valid user | 200/201 | 000 | FAIL
| 2 | /auth/login | POST | valid creds | 200 | 000 | FAIL
| 3 | /auth/register | POST | empty fields | 422 | 000 | FAIL
| 4 | /auth/login | POST | wrong pass | 401 | 000 | FAIL
## Verdict: FAIL
Specific failures: All tests failed with HTTP status code 000.