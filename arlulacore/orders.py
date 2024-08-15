'''
    Defines the OrdersAPI
'''

from datetime import datetime
import os
import typing
import json
import requests
import sys
import re

from .list import ListRequest, ListResponse
from .auth import Session
from .exception import ArlulaAPIException
from .util import parse_rfc3339, simple_indent
from .dataset import Dataset, get_dataset_id
from .order import Order, get_order_id
from .resource import Resource, get_resource_id
from .campaign import Campaign, get_campaign_id

disposition_name_regex = re.compile(r"\"([\w\.]+)\"")

class OrdersAPI:
    '''
        Orders is used to interface with the Arlula Orders API.
        Allows for access to Orders, Campaigns, Datasets, and Resources.
    '''

    def __init__(self, session: Session):
        self.session = session
        self.url = self.session.baseURL + "/api"
    
    def list_orders(self, 
        req: typing.Optional[ListRequest] = None,
    ) -> ListResponse[Order]:
        """
            List all orders that the API account making this request has access to.
            The orders will not have their campaigns or datasets populated.
        """

        url = self.url + "/orders"
        response = requests.request(
            "GET",
            url,
            headers=self.session.header,
            params=req.__dict__() if req != None else None,
        )

        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            d = json.loads(response.text)
            orders = [Order(c) for c in d["content"]]
            l = ListResponse[Order](d, orders)
            return l
    
    def list_datasets(self, 
        req: typing.Optional[ListRequest] = None,
    ) -> ListResponse[Dataset]:
        """
            List all datasets that the API account making this request has access to.
            The datasets will not have their resources populated.
        """

        url = self.url + "/datasets"
        response = requests.request(
            "GET",
            url,
            headers=self.session.header,
            params=req.__dict__() if req != None else None,
        )

        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            d = json.loads(response.text)
            datasets = [Dataset(c) for c in d["content"]]
            l = ListResponse[Dataset](d, datasets)
            return l
    
    def list_campaigns(self, 
        req: typing.Optional[ListRequest] = None,
    ) -> ListResponse[Campaign]:
        """
            List all campaigns that the API account making this request has access to.
            The campaigns will not have their datasets populated.
        """

        url = self.url + "/campaigns"
        response = requests.request(
            "GET",
            url,
            headers=self.session.header,
            params=req.__dict__() if req != None else None,
        )

        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            d = json.loads(response.text)
            campaigns = [Campaign(c) for c in d["content"]]
            l = ListResponse[Campaign](d, campaigns)
            return l

    def list_order_campaigns(self, 
        order: typing.Union[str, Order],
    ) -> ListResponse[Campaign]:
        """
            List all campaigns for the specified order.
            The campaigns will not have their datasets populated.
        """

        response = requests.request(
            "GET",
            self.url + f"/order/{get_order_id(order)}/campaigns",
            headers=self.session.header,
        )
        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            d = json.loads(response.text)
            campaigns = [Campaign(c) for c in d["content"]]
            l = ListResponse[Campaign](d, campaigns)
            return l

    def list_order_datasets(self, 
        order: typing.Union[str, Order],
    ) -> ListResponse[Dataset]:
        """
            List all datasets for the specified order.
            Will return any archive datasets ordered and any datasets delivered to
            campaigns within the order.
            The datasets will not have their resources populated.
        """

        response = requests.request(
            "GET",
            self.url + f"/order/{get_order_id(order)}/datasets",
            headers=self.session.header,
        )
        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            d = json.loads(response.text)
            datasets = [Dataset(c) for c in d["content"]]
            l = ListResponse[Dataset](d, datasets)
            return l

    def list_campaign_datasets(self,
        campaign: typing.Union[str, Campaign]                           
    ) -> ListResponse[Dataset]:
        """
            List all datasets delivered for a specified campaign.
            The datasets will not have their resources populated.
        """

        response = requests.request(
            "GET",
            self.url + f"/campaign/{get_campaign_id(campaign)}/datasets",
            headers=self.session.header,
        )
        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            d = json.loads(response.text)
            campaigns = [Dataset(c) for c in d["content"]]
            l = ListResponse[Dataset](d, campaigns)
            return l
        
    def get_order(self, order: typing.Union[str, Order]) -> Order:
        """
            Get the specified order.
            Guarantees campaigns and datasets are correct. 
        """

        response = requests.request(
            "GET",
            self.url + f"/order/{get_order_id(order)}",
            headers=self.session.header,
        )
        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            return Order(json.loads(response.text))
        
        
    def get_campaign(self, campaign: typing.Union[str, Campaign]) -> Campaign:
        """
            Get the specified campaign.
            Guarantees datasets are correct.
        """

        response = requests.request(
            "GET",
            self.url + f"/campaign/{get_campaign_id(campaign)}",
            headers=self.session.header,
        )
        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            return Campaign(json.loads(response.text))

    def get_dataset(self, dataset: typing.Union[str, Dataset]) -> Dataset:
        """
            Get the specified dataset.
            Guarantees the resources are correct.
        """

        response = requests.request(
            "GET",
            self.url + f"/dataset/{get_dataset_id(dataset)}",
            headers=self.session.header,
        )
        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            return Dataset(json.loads(response.text))
        
    def get_resource(self, resource: typing.Union[str, Resource]) -> Resource:
        """
            Get the specified resource.
        """

        response = requests.request(
            "GET",
            self.url + f"/resource/{get_resource_id(resource)}",
            headers=self.session.header,
        )
        if response.status_code != 200:
            raise ArlulaAPIException(response)
        else:
            return Resource(json.loads(response.text))


    def download_dataset(self, 
        dataset: typing.Union[str, Dataset], 
        directory: typing.Optional[str], 
        suppress: typing.Optional[bool]=False,
    ) -> None:
        dataset = self.get_dataset(dataset)
        for r in dataset.resources:
            self.download_resource_as_file(r.id, suppress=suppress, directory=directory).close()

    def download_resource_as_file(self,
            resource: typing.Union[str, Resource],
            filepath: typing.Optional[str] = None,
            suppress: typing.Optional[bool] = False,
            progress_generator: typing.Optional[typing.Generator[typing.Optional[float], None, None]] = None,
            directory: typing.Optional[str] = None,
        ) -> typing.BinaryIO:
        '''
            Get a resource and stream it to the specified file. If supress is False, it will output extra information to standard output.
            If filename is not supplied, it will use the file specified by the supplier through the Content-Disposition header. If a filename
            is not supplied and a directory is then the default named file will be placed in the specified directory, otherwise it is ignored.
            This is recommended for large files. Returns the file, which must be closed. The returned file is seeked back to it's beginning.
        '''

        url = self.url + f"/resource/{get_resource_id(resource)}/data"

        if progress_generator is not None:
            next(progress_generator)

        # Stream response
        response = requests.request(
            "GET",
            url,
            headers=self.session.header,
            stream=True)
        
        if response.status_code != 200:
            raise ArlulaAPIException(response)

        if filepath is None:
            # As requests follows redirects, need to use the history
            content_disposition = response.history[0].headers.get("content-disposition")
            filename = disposition_name_regex.findall(content_disposition)[0]
            dir = directory or os.getcwd()
            filepath = os.path.join(dir, filename)
        f = open(filepath, "w+b")

        total = response.headers.get('content-length')


        if total is None:
            f.write(response.content)
        else:
            # Write the response in chunks
            # Chunk size is the larger of 0.1% of the filesize or 1MB
            downloaded = 0
            total = int(total)
            
            for data in response.iter_content(chunk_size=max(int(total/1000), 1024*1024)):
                downloaded += len(data)
                f.write(data)

                # Track progress of download
                done = int(50*downloaded/total)
                if not suppress:
                    sys.stdout.write('\r[{}{}]{:.2%}'.format(
                        '█' * done, '.' * (50-done), downloaded/total))
                    sys.stdout.flush()
                if progress_generator is not None:
                    progress_generator.send(downloaded/total)

        if not suppress:
            sys.stdout.write('\n')
            sys.stdout.write('download complete\n')

        # So the file is able to be read from the beginning.
        f.seek(0)
        
        return f

    def download_resource_as_memory(self, resource: typing.Union[str, Resource]) -> bytes:
        '''
            Get a resource. If filepath is specified, it will be streamed to that file. If filepath is omitted it will
            be stored in memory (not recommended for large files).
        '''
        url = self.url + f"/resource/{get_resource_id(resource)}/data"

        response = requests.request(
            "GET",
            url,
            headers=self.session.header)
        
        if response.status_code != 200:
            raise ArlulaAPIException(response)

        return response.content
