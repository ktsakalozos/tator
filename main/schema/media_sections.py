from rest_framework.schemas.openapi import AutoSchema

from ._media_query import media_filter_parameter_schema
from ._attributes import attribute_filter_parameter_schema

class MediaSectionsSchema(AutoSchema):
    def get_operation(self, path, method):
        operation = super().get_operation(path, method)
        operation['tags'] = ['Media']
        return operation

    def _get_path_parameters(self, path, method):
        return [{
            'name': 'project',
            'in': 'path',
            'required': True,
            'description': 'A unique integer identifying a project.',
            'schema': {'type': 'integer'},
        }]

    def _get_filter_parameters(self, path, method):
        params = []
        if method  == 'GET':
            params = media_filter_parameter_schema + attribute_filter_parameter_schema
        return params

    def _get_request_body(self, path, method):
        return {}

    def _get_responses(self, path, method):
        responses = {}
        responses['404'] = {'description': 'Failure to find project with given ID.'}
        responses['400'] = {'description': 'Bad request.'}
        if method == 'GET':
            responses['200'] = {
                'description': 'Successful retrieval of media count per section.',
                'content': {'application/json': {'schema': {
                    'type': 'object',
                    'additionalProperties': {
                        'type': 'object',
                        'properties': {
                            'num_videos': {'type': 'integer', 'minimum': 0},
                            'num_images': {'type': 'integer', 'minimum': 0},
                        },
                    },
                }}}
            }
        return responses
