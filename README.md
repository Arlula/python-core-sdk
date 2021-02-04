# **Arlula API Python Package**
## About
This package provides a core interface for interacting with the Arlula API. For a more full-featured package, see [arlulaapi](https://pypi.org/project/arlulaapi/).

## Prerequisites
This package requires an active Arlula account and access to the API credentials. If you don't have an account, you can create one at [api.arlula.com/signup](https://api.arlula.com/signup).

## Installation
```bash
pip install arlulacore
```
## Initiation
Instantiate a Session object using your API credentials as below. This will validate your credentials and store them for the remainder of the session.
```python
import arlulacore

"""opening a session"""
arlula_session = arlulacore.Session(key, secret)
```

## API Endpoints
This package contains methods for each of the supported API endpoints, namespaced by API namespace. Each namespace inherits the session defined above
### Archive
```python
archive = arlulacore.Archive(arlula_session)

search_result = archive.search(
    start="string",
    end="string"
    res="string",
    lat=float,
    long=float,
    north=float,
    south=float,
    east=float,
    west=float
)

order = archive.order(
    id=imageryId,
    eula="",
    seats=1,
    webhooks=[...],
    emails=[...]
)
```
### Orders
```python
orders = arlulacore.Orders(arlula_session)

order = orders.get(
    id=orderId
)

orders.get_resource(
    id=resourceId,
    filepath="downloads/thumbnail.jpg",
    # optional
    suppress="false"
)

order_list = orders.list_orders()
```