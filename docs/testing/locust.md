# Load Testing with Locust

This document outlines how to perform load testing on the Tempo API using [Locust](https://locust.io/). Locust is an open-source load testing tool that allows you to define user behavior with Python code and then simulate millions of concurrent users.

## Locust example

Open `locustfile.py` in the root directory of the project that simulates a load test for wallets and transactions.

To run the test:

```bash
locust --headless -f locustfile.py -H http://127.0.0.1:8000 --users 5 --run-time 10m --html report.locust.html
```
