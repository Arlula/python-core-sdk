# **Arlula API Python Package**
## About
This package provides a core interface for interacting with the [Arlula API](https://www.arlula.com/documentation/).
This package can be found on [PyPI](https://pypi.org/project/arlulacore/).
Documentation for this package can be found below, but for extensive documentation see the [wiki](https://github.com/Arlula/python-core-sdk/wiki).

## Prerequisites
This package requires an active Arlula account and access to the API credentials. If you don't have an account, you can create one at [api.arlula.com/signup](https://api.arlula.com/signup).

## Installation
```bash
pip install arlulacore
```
## Instantiation
Instantiate a Session object using your API credentials as below. This will validate your credentials and store them for the remainder of the session. This can be re-used for numerous requests or be instantiated numerous times with different API account credentials for concurrent access to different sessions.
```python
import arlulacore

"""opening a session"""
arlula_session = arlulacore.Session(key, secret)
```

## API Endpoints
This package contains methods for each of the supported API endpoints, namespaced by API namespace. Each namespace inherits the session defined above

### Archive

The Archive API provides the ability to search and order from Arlula and its supplier's historic imagery archives.

```python
api = arlulacore.ArlulaAPI(arlula_session)

archive = api.archiveAPI()

# Search for imagery around sydney between 2020-Jan-1 and 2020-Feb-1
# With at least 10m resolution (gsd)
search_result = archive.search(
    arlulacore.SearchRequest(
        start=date(2020, 1, 1), 
        gsd=10,
    )
    .set_point_of_interest(-33.8688, 151.2093)
    .set_end(date(2020, 2, 1))
)

# Order a specific image from the archive, using the id from above, 
# the eula that applies to you, the bundle you want, and (optionally) 
# email jane.doe@gmail.com and john.smith@gmail.com when it is complete.
order_result = archive.order(
    arlulacore.ArchiveOrderRequest(
        id="eyJhb...AYTqwM",
        eula="Supplier's EULA",
        bundle_key="default",
    )
    .set_emails(["john.smith@gmail.com", "jane.doe@gmail.com"])
)
```

### Tasking

The Tasking API provides the ability to search and order future capturing opportunities from Arlula and it's suppliers.

```python
tasking = api.taskingAPI()

# Search for capturing opportunities around sydney over the next 30 days
# With at least 1m resolution and at an off-nadir of less than 30 degrees.
search_result = tasking.search(
    arlulacore.TaskingSearchRequest(
        datetime.datetime.now(datetime.timezone.utc), 
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30),
        1,
        30,
    )
    .set_point_of_interest(-33.8688, 151.2093)
)

# Order a future capture, using the ordering id from an above result, 
# the eula that applies to you, the bundle you want, and (optionally) 
# email jane.doe@gmail.com and john.smith@gmail.com when it is complete.
order_result = tasking.order(
    arlulacore.TaskingOrderRequest(
        id="eyJhb...AYTqwM",
        eula="Supplier's EULA",
        bundle_key="default",
        priority="priority",
        cloud=30,
    )
    .set_emails(["john.smith@gmail.com", "jane.doe@gmail.com"])
)
```

### Orders

The Orders API provides the ability to list and get entities within Arlula's Orders system.
These include Orders, Datasets, Campaigns, and Resources. 

```python
ordersAPI = api.ordersAPI()

# List all orders the authenticated API account has access to
orders = ordersAPI.list_orders()

# Get all campaigns delivered for an order
campaigns = ordersAPI.list_campaigns_for_order("cade11f4-8b4d-43e1-8cb1-3bce85111a01")

# Get all datasets delivered for an order
datasets = ordersAPI.list_datasets_for_order("cade11f4-8b4d-43e1-8cb1-3bce85111a01")

# Get the status and details of an order (will also populate datasets and campaigns)
order = ordersAPI.get_order("cade11f4-8b4d-43e1-8cb1-3bce85111a01")

# List all datasets the authenticated API account has access to
datasets = ordersAPI.list_datasets()

# Get a specific resource, for example thumbnails, tiffs, json metadata.
# Streams to a file and returns the file handle.
with ordersAPI.download_resource_as_file("b7adb198-3e6e-4217-9e67-fb26eb355cc4", filepath="downloads/thumbnail.jpg") as f:
    f.read()

# Get a specific resource, for example thumbnails, tiffs, json metadata.
# Returns the memory buffer of the requested resource.
# Not recommended for large files.
b = ordersAPI.download_resource_as_memory("b7adb198-3e6e-4217-9e67-fb26eb355cc4")

```
