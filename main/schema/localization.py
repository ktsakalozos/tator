from rest_framework.schemas.openapi import AutoSchema

from ._attributes import attribute_filter_parameter_schema
from ._annotation_query import annotation_filter_parameter_schema

localization_properties = {
    'x': {
        'description': 'Normalized horizontal position of left edge of bounding box for '
                       '`box` localization types, start of line for `line` localization '
                       'types, or position of dot for `dot` localization types.',
        'type': 'number',
        'minimum': 0.0,
        'maximum': 1.0,
        'nullable': True,
    },
    'y': {
        'description': 'Normalized vertical position of top edge of bounding box for '
                       '`box` localization types, start of line for `line` localization '
                       'types, or position of dot for `dot` localization types.',
        'type': 'number',
        'minimum': 0.0,
        'maximum': 1.0,
        'nullable': True,
    },
    'width': {
        'description': 'Normalized width of bounding box for `box` localization types.',
        'type': 'number',
        'minimum': 0.0,
        'maximum': 1.0,
        'nullable': True,
    },
    'height': {
        'description': 'Normalized height of bounding box for `box` localization types.',
        'type': 'number',
        'minimum': 0.0,
        'maximum': 1.0,
        'nullable': True,
    },
    'u': {
        'description': 'Horizontal vector component for `line` localization types.',
        'type': 'number',
        'minimum': -1.0,
        'maximum': 1.0,
        'nullable': True,
    },
    'v': {
        'description': 'Vertical vector component for `line` localization types.',
        'type': 'number',
        'minimum': -1.0,
        'maximum': 1.0,
        'nullable': True,
    },
    'frame': {
        'description': 'Frame number of this localization if it is in a video.',
        'type': 'integer',
        'default': 0,
    },
    'parent': {
        'description': 'If a clone, the pk of the parent.',
        'type': 'number',
        'nullable': True,
    },
    'attributes': {
        'description': 'Object containing attribute values.',
        'type': 'object',
        'additionalProperties': True,
    }
}

localization_filter_schema = [
    {
        'name': 'excludeParents',
        'in': 'query',
        'required': False,
        'description': 'If a clone is present, do not send parent. (0 or 1)',
        'schema': {'type': 'integer',
                   'minimum': 0,
                   'maximum': 1,
                   'default': 0
                   }
    },
]

class LocalizationListSchema(AutoSchema):
    def get_operation(self, path, method):
        operation = super().get_operation(path, method)
        operation['tags'] = ['Localization']
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
        if method in ['GET', 'PATCH', 'DELETE']:
            params = annotation_filter_parameter_schema + attribute_filter_parameter_schema + localization_filter_schema
        return params

    def _get_request_body(self, path, method):
        body = {}
        if method == 'POST':
            body = {'content': {'application/json': {
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'additionalProperties': True,
                        'properties': {
                            'media_id': {
                                'description': 'Unique integer identifying a media.',
                                'type': 'integer',
                            },
                            'type': {
                                'description': 'Unique integer identifying a localization type.',
                                'type': 'integer',
                            },
                            'version': {
                                'description': 'Unique integer identifying the version.',
                                'type': 'integer',
                            },
                            'modified': {
                                'description': 'Whether this localization was created in the web UI.',
                                'type': 'boolean',
                                'nullable': True,
                            },
                            **localization_properties,
                        },
                    },
                },
                'examples': {
                    'box': {
                        'summary': 'Single box localization',
                        'value': [{
                            'media_id': 1,
                            'type': 1,
                            'x': 0.1,
                            'y': 0.2,
                            'width': 0.3,
                            'height': 0.4,
                            'frame': 1000,
                            'My First Attribute': 'value1',
                            'My Second Attribute': 'value2',
                        }],
                    },
                    'boxes': {
                        'summary': 'Many box localizations',
                        'value': [
                            {
                                'media_id': 1,
                                'type': 1,
                                'x': 0.1,
                                'y': 0.2,
                                'width': 0.3,
                                'height': 0.4,
                                'frame': 100,
                                'My First Attribute': 'value1',
                                'My Second Attribute': 'value2',
                            },
                            {
                                'media_id': 1,
                                'type': 1,
                                'x': 0.1,
                                'y': 0.2,
                                'width': 0.3,
                                'height': 0.4,
                                'frame': 1000,
                                'My First Attribute': 'value1',
                                'My Second Attribute': 'value2',
                            },
                        ],
                    },
                    'line': {
                        'summary': 'Single line localization',
                        'value': [{
                            'media_id': 1,
                            'type': 2,
                            'x': 0.1,
                            'y': 0.2,
                            'u': 0.3,
                            'v': 0.4,
                            'frame': 1000,
                            'My First Attribute': 'value1',
                            'My Second Attribute': 'value2',
                        }],
                    },
                    'lines': {
                        'summary': 'Many line localizations',
                        'value': [
                            {
                                'media_id': 1,
                                'type': 2,
                                'x': 0.1,
                                'y': 0.2,
                                'u': 0.3,
                                'v': 0.4,
                                'frame': 100,
                                'My First Attribute': 'value1',
                                'My Second Attribute': 'value2',
                            },
                            {
                                'x': 0.1,
                                'y': 0.2,
                                'u': 0.3,
                                'v': 0.4,
                                'frame': 1000,
                                'My First Attribute': 'value1',
                                'My Second Attribute': 'value2',
                            },
                        ],
                    },
                    'dot': {
                        'summary': 'Single dot localization',
                        'value': [{
                            'media_id': 1,
                            'type': 1,
                            'x': 0.1,
                            'y': 0.2,
                            'frame': 1000,
                            'My First Attribute': 'value1',
                            'My Second Attribute': 'value2',
                        }],
                    },
                    'dots': {
                        'summary': 'Many dot localizations',
                        'value': [
                            {
                                'media_id': 1,
                                'type': 1,
                                'x': 0.1,
                                'y': 0.2,
                                'frame': 100,
                                'My First Attribute': 'value1',
                                'My Second Attribute': 'value2',
                            },
                            {
                                'x': 0.1,
                                'y': 0.2,
                                'frame': 1000,
                                'My First Attribute': 'value1',
                                'My Second Attribute': 'value2',
                            },
                        ],
                    },
                }
            }}}
        if method == 'PATCH':
            body = {'content': {'application/json': {
                'schema': {
                    'type': 'object',
                    'required': ['attributes'],
                    'properties': {
                        'attributes': {
                            'description': 'Attribute values to bulk update.',
                            'type': 'object',
                            'additionalProperties': True,
                        },
                    },
                },
                'examples': {
                    'single': {
                        'summary': 'Update Species attribute of many localizations',
                        'value': {
                            'attributes': {
                                'Species': 'Tuna',
                            }
                        },
                    },
                }
            }}}
        return body

    def _get_responses(self, path, method):
        responses = {}
        responses['404'] = {'description': 'Failure to find project with given ID.'}
        responses['400'] = {'description': 'Bad request.'}
        if method == 'GET':
            responses['200'] = {'description': 'Successful retrieval of localization list.'}
        elif method == 'POST':
            responses['201'] = {'description': 'Successful creation of localization(s).'}
        elif method == 'PATCH':
            responses['200'] = {'description': 'Successful bulk update of localization '
                                               'attributes.'}
        elif method == 'DELETE':
            responses['204'] = {'description': 'Successful bulk delete of localizations.'}
        return responses

class LocalizationDetailSchema(AutoSchema):
    def get_operation(self, path, method):
        operation = super().get_operation(path, method)
        operation['tags'] = ['Localization']
        return operation

    def _get_path_parameters(self, path, method):
        return [{
            'name': 'id',
            'in': 'path',
            'required': True,
            'description': 'A unique integer identifying a localization.',
            'schema': {'type': 'integer'},
        }]

    def _get_filter_parameters(self, path, method):
        return []

    def _get_request_body(self, path, method):
        body = {}
        if method == 'PATCH':
            body = {'content': {'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        **localization_properties,
                        'modified': {
                            'description': 'Whether this localization was created in the web UI.',
                            'type': 'boolean',
                            'nullable': True,
                        },
                    },
                },
                'example': {
                    'x': 0.25,
                    'y': 0.25,
                    'width': 0.25,
                    'height': 0.25,
                }
            }}}
        return body

    def _get_responses(self, path, method):
        responses = super()._get_responses(path, method)
        responses['404'] = {'description': 'Failure to find localization with given ID.'}
        responses['400'] = {'description': 'Bad request.'}
        if method == 'PATCH':
            responses['200'] = {'description': 'Successful update of localization.'}
        if method == 'DELETE':
            responses['204'] = {'description': 'Successful deletion of localization.'}
        return responses

