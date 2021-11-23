import typing

class ArlulaObject:
    def __repr__(self):
        return str(['{}: {}'.format(attr, value) for attr, value in self.__dict__.items()])[1:-1].replace('\'', '')

class Resource(ArlulaObject):
    id: str
    created_at: str
    updated_at: str
    order: str
    name: str
    type: str
    format: str
    roles: typing.List[str]
    size: int
    checksum: str

    def __init__(self, data):
        self.id = data["id"]
        self.created_at = data["createdAt"]
        self.updated_at = data["updatedAt"]
        self.order = data["order"]
        self.name = data["name"]
        self.type = data["type"]
        self.format = data["format"]
        self.roles = data["roles"]
        self.size = data["size"]
        self.checksum = data["checksum"]

class OrderResult(ArlulaObject):
    id: str
    created_at: str
    updated_at: str
    supplier: str
    imagery_id: str
    scene_id: str
    status: str
    total: int
    type: str
    expiration: typing.Optional[str]

    def __init__(self, data):
        self.id = data["id"]
        self.created_at = data["createdAt"]
        self.updated_at = data["updatedAt"]
        self.supplier = data["supplier"]
        self.imagery_id = data["imageryID"]
        self.scene_id = data["sceneID"]
        self.status = data["status"]
        self.total = data["total"]
        self.type = data["type"]
        self.expiration = data["expiration"]

class DetailedOrderResult(ArlulaObject):
    id: str
    created_at: str
    updated_at: str
    supplier: str
    imagery_id: str
    scene_id: str
    status: str
    total: int
    type: str
    expiration: typing.Optional[str]
    resources: typing.List[Resource]

    def __init__(self, data):
        self.id = data["id"]
        self.created_at = data["createdAt"]
        self.updated_at = data["updatedAt"]
        self.supplier = data["supplier"]
        self.imagery_id = data["imageryID"]
        self.scene_id = data["sceneID"]
        self.status = data["status"]
        self.total = data["total"]
        self.type = data["type"]
        self.expiration = data["expiration"]
        self.resources = [Resource(x) for x in data["resources"]]