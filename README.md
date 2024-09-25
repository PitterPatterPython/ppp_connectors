# Connectors
A simple, lightweight set of connectors and functions to various APIs, controlled by a central broker.

## How to install
1. Install via pip to your environment: `pip install ppp-connectors`
2. Load the required environment variables into your environment. You can find these in `env.sample`. This library is intelligent enough to look for both a `.env` file _and_ within your system's environment variables, so you can do either option.

## Passing additional parameters to a function
All functions will accept `**kwargs` as additional parameters. For example, the URLScan.io `/search` endpoint accepts a `size` parameter. You can include additional parameters like this:
```python
from ppp_connectors import urlscan
r = urlscan.urlscan_search('domain:google.com', **{'size': 200})
print(r.json())
```
Every individual API is different, so apply additional parameters after consulting the appropriate vendor's API documentation