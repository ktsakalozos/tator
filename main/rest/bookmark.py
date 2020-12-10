""" Bookmark REST endpoints """
# pylint: disable=too-many-ancestors

import logging

from django.db import transaction

from ..models import Project
from ..models import User
from ..models import Bookmark
from ..models import database_qs
from ..schema import BookmarkDetailSchema
from ..schema import BookmarkListSchema
from ..schema import parse

from ._base_views import BaseDetailView
from ._base_views import BaseListView
from ._permissions import ProjectEditPermission

logger = logging.getLogger(__name__)

class BookmarkListAPI(BaseListView):
    """ Retrieves bookmarks saved by a user
    """
    # pylint: disable=no-member,no-self-use
    schema = BookmarkListSchema()
    permission_classes = [ProjectEditPermission]
    http_method_names = ['get', 'post']

    def _get(self, params: dict) -> dict:
        """ Returns the full database entries of bookmarks registered with this project
            and user.
        """
        qs = Bookmark.objects.filter(project=params['project'],
                                     user=self.request.user).order_by('id')
        return database_qs(qs)

    def get_queryset(self):
        """ Returns a queryset of bookmarks related with the current request's project
        """
        params = parse(self.request)
        qs = Bookmark.objects.filter(project__id=params['project'],
                                     user=self.request.user)
        return qs

    def _post(self, params: dict) -> dict:
        """ Saves a new bookmark.
        """
        # Save the bookmark.
        fave = Bookmark.objects.create(
            name=params['name'],
            project=Project.objects.get(pk=params['project']),
            user=self.request.user,
            uri=params['uri'],
        )
        return {'message': 'Successfully created bookmark {fave.id}!.', 'id': fave.id}

class BookmarkDetailAPI(BaseDetailView):
    """ Interact with a single bookmark
    """

    schema = BookmarkDetailSchema()
    permission_classes = [ProjectEditPermission]
    http_method_names = ['get', 'patch', 'delete']

    def _get(self, params):
        """ Retrieve the requested algortihm entry by ID
        """
        return database_qs(Bookmark.objects.filter(pk=params['id']))[0]

    @transaction.atomic
    def _patch(self, params) -> dict:
        """ Patch operation on the algorithm entry
        """
        obj = Bookmark.objects.select_for_update().get(pk=params['id'])
        name = params.get('name', None)
        if name is not None:
            obj.name = name
        obj.save()
        return {'message': f'Bookmark {obj.id} updated successfully!'}

    def _delete(self, params: dict) -> dict:
        """ Deletes the provided bookmark.
        """
        Bookmark.objects.get(pk=params['id']).delete()
        return {'message': f"Bookmark with ID {params['id']} deleted successfully!"}

    def get_queryset(self):
        """ Returns a queryset of all registered algorithms
        """
        return Bookmark.objects.all()
