# QA Test Report
## Code Review
* No major issues found
## Unit Test Results
* 1 test passed
## Live API Test Results
| # | Endpoint | Method | Payload | Expected | Actual Status | Result |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | /auth/register | POST | valid user | 200/201 | 000 | FAIL |
## Verdict
FAIL
* /auth/register endpoint failed with status code 000