from pyapiary.api_connectors.urlscan import URLScanConnector, AsyncURLScanConnector

urlscan = URLScanConnector(
    load_env_vars=True,
    trust_env=True,
    verify=False,
    enable_logging=True
)

urlscan_async = AsyncURLScanConnector(
    load_env_vars=True,
    trust_env=True,
    verify=False,
    enable_logging=True
)

sample_scan_uuid = "0198d378-c19e-707c-add7-45c289b2851c"


# ---------- sync ----------
res = urlscan.search("google.com")
print(res.status_code)

res = urlscan.scan("google.com")
print(res.status_code)

res = urlscan.results(sample_scan_uuid)
print(res.status_code)

res = urlscan.get_dom(sample_scan_uuid)
print(res.status_code)

res = urlscan.structure_search(sample_scan_uuid)
print(res.status_code)