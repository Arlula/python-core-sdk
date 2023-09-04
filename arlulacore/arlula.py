from .auth import Session
from .archive import ArchiveAPI
from .orders import OrdersAPI
from .collections import CollectionsAPI
from .tasking import TaskingAPI

class ArlulaAPI:
    '''
        Main class for Arlula API Calls. Contains an instance of the archive and orders APIs.
    '''

    def __init__(self, session: Session):
        self._archive = ArchiveAPI(session)
        self._orders = OrdersAPI(session)
        self._collections = CollectionsAPI(session)
        self._tasking = TaskingAPI(session)
    
    def archiveAPI(self) -> ArchiveAPI:
        '''
            Returns the archive api instance, used for searching and ordering imagery.
        '''
        return self._archive

    def ordersAPI(self) -> OrdersAPI:
        '''
            Returns the orders api instance, used for maintaining orders and getting resources.
        '''
        return self._orders
    
    def collectionsAPI(self) -> CollectionsAPI:
        """
            Returns the collections api instance, used for maintaining collections and their items.
        """
        return self._collections

    def taskingAPI(self) -> TaskingAPI:
        """
            Returns the tasking api instance, used for searching for and ordering future captures.
        """
        return self._tasking
