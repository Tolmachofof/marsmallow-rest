# -*- coding: utf-8 -*-

import re

from marshmallow import fields
from marshmallow.utils import get_value, missing


class HateoasMixin(object):
    """Mixin that provides functionality for field visibility control."""
    
    def __init__(self, *args, hateoas=True, **kwargs):
        if not isinstance(hateoas, bool) and not callable(hateoas):
            raise ValueError(
                'The hateoas param must be a boolean or callable!'
            )
        self.hateoas = hateoas
        super(HateoasMixin, self).__init__(*args, **kwargs)
        
    def is_visible(self, obj, context):
        if isinstance(self.hateoas, bool):
            return self.hateoas
        is_visible = self.hateoas(obj, context)
        if not isinstance(is_visible, bool):
            raise ValueError(
                'The hateoas function must return a boolean instance!'
            )
        return is_visible


class LinkField(HateoasMixin, fields.Field):
    
    _CHECK_ATTRIBUTE = False
    
    def __init__(self, link_tpl, method='GET', title='', **kwargs):
        self.link_tpl = link_tpl
        self.method = method
        self.title = title
        super(LinkField, self).__init__(**kwargs)
        
    def _serialize(self, value, attr, obj):
        return {
            'href': self._render_link_tpl(obj, self.context),
            'method': self.method,
            'title': self.title
        }
    
    def _render_link_tpl(self, obj, context):
        link = self.link_tpl
        for bound_attr in set(re.findall(r'<\w*>', link)):
            attr_name = bound_attr.strip('<>')
            value = get_value(attr_name, obj)
            if value is missing:
                value = context.get(attr_name, missing)
            if value is missing:
                raise AttributeError(
                    '{} is not a valid attribute of object: {},'
                    ' context: {}'.format(bound_attr, obj, context)
                )
            link = link.replace(bound_attr, str(value))
        return link

        
class HyperLinks(HateoasMixin, fields.Field):
    
    _CHECK_ATTRIBUTE = False

    def __init__(self, schema, **kwargs):
        if not isinstance(schema, dict):
            raise ValueError('The schema param must be a dict instance!')
        self.schema = schema
        super(HyperLinks, self).__init__(**kwargs)
        
    def _add_to_schema(self, field_name, schema):
        super(HyperLinks, self)._add_to_schema(field_name, schema)
        for resource in self.schema.values():
            resource.parent = self
        
    def _serialize(self, value, attr, obj):
        return {
            name: resource.serialize(name, obj)
            for name, resource in self.schema.items()
            if resource.is_visible(obj, self.context)
        }
