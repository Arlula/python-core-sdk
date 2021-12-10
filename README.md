# **Arlula API Python Package**
## About
This package provides a core interface for interacting with the [Arlula API](https://www.arlula.com/documentation/).
This package can be found on [PyPI](https://pypi.org/project/arlulacore/).

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
api = arlulacore.ArlulaAPI(arlula_session)

archive = api.archiveAPI()

# Search for imagery around sydney between 2020-Jan-1 and 2020-Feb-1
# With at least 10m resolution
search_result = archive.search(
    arlulacore.SearchRequest(
        start=date(2020, 1, 1), 
        res=10,
    )
    .set_point_of_interest(-33.8688, 151.2093)
    .set_end(date(2020, 2, 1))
)

# Order a specific image from the archive, using the id from above, and (optionally) 
# email jane.doe@gmail.com and john.smith@gmail.com when it is complete.
order_result = archive.order(
    arlulacore.OrderRequest(
        id="cade11f4-8b4d-43e1-8cb1-3bce85111a01",
        eula="Supplier's EULA",
        seats=1,
    )
    .set_emails(["john.smith@gmail.com", "jane.doe@gmail.com"])
)
```
### Orders
```python
orders = api.ordersAPI()

# Get the status and details of an order
order = orders.get(
    id="cade11f4-8b4d-43e1-8cb1-3bce85111a01",
)

# Get a specific resource, for example thumbnails, tiffs, json metadata.
# Streams to a file and returns the file handle.
f = orders.get_resource_as_file(
    id="b7adb198-3e6e-4217-9e67-fb26eb355cc4",
    filepath="downloads/thumbnail.jpg",
)

# Get a specific resource, for example thumbnails, tiffs, json metadata.
# Returns the memory buffer of the requested resource.
# Not recommended for large files.
b = orders.get_resource_as_memory(
    id="b7adb198-3e6e-4217-9e67-fb26eb355cc4",
)

# List the details and status of all orders made
order_list = orders.list_orders()
```