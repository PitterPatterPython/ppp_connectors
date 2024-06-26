from broker import make_request


def sip_cookie_domains(cookie_domains, **kwargs):
    method = "get"
    url = "https://test"
    headers = {}
    payload = {}

    make_request(method=method, url=url, headers=headers, payload=payload)


if __name__ == "__main__":
    sip_cookie_domains("test")
