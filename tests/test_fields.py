# -*- coding: utf-8 -*-

from collections import namedtuple
from unittest import mock

import pytest

from marshmallow_rest.fields import LinkField


Author = namedtuple('Author', ('id', 'name'))


@pytest.mark.parametrize(
    'link_tpl, obj, context, expected', (
        ('/authors', {}, {}, '/authors'),
        ('/authors', {'id': 1}, {'id': 2}, '/authors'),
        ('/authors', Author(1, 'William Shakespeare'), {}, '/authors'),
        ('/authors/<id>', Author(1, 'William Shakespeare'), {}, '/authors/1'),
        ('/authors/<id>', {'id': 1}, {}, '/authors/1'),
        ('/authors/<id>', {}, {'id': 1}, '/authors/1'),
        (
            '/authors/<id>',
            Author(1, 'William Shakespeare'), {'id': 2},
            '/authors/1'
        ),
        ('/authors/<id>', {'id': 1}, {'id': 2}, '/authors/1'),
        (
            '/books/<author_id>/<state>',
            {'author_id': 1}, {'state': 'published'},
            '/books/1/published'
        )
    )
)
def test_render_link_tpl(link_tpl, obj, context, expected):
    field = LinkField(link_tpl)
    assert field._render_link_tpl(obj, context) == expected


@pytest.mark.parametrize(
    'link_tpl, obj, context', (
        ('/authors/<id>', {}, {}),
        ('/authors/<>', {}, {}),
        ('/authors/<name>', {'id': 1}, {}),
        ('/authors/<name>', {}, {'id': 1})
    )
)
def test_render_link_raises_exception(link_tpl, obj, context):
    field = LinkField(link_tpl)
    with pytest.raises(AttributeError):
        field._render_link_tpl(obj, context)


@pytest.mark.parametrize(
    'link_tpl, kwargs, obj, context, expected', (
        (
            '/author',
            {}, Author(1, 'William Shakespeare'), {},
            {'href': '/author', 'method': 'GET', 'title': ''}
        ),
        (
            '/author',
            {'method': 'POST'}, Author(1, 'William Shakespeare'), {},
            {'href': '/author', 'method': 'POST', 'title': ''}
        ),
        (
            '/author',
            {'method': 'POST', 'title': 'Create author'},
            Author(1, 'William Shakespeare'), {},
            {'href': '/author', 'method': 'POST', 'title': 'Create author'}
        ),
        (
            '/author/<id>',
            {}, Author(1, 'William Shakespeare'), {},
            {'href': '/author/1', 'method': 'GET', 'title': ''}
        ),
        (
            '/author/<id>',
            {}, {'id': 1}, {},
            {'href': '/author/1', 'method': 'GET', 'title': ''}
        ),
        (
            '/author/<id>',
            {}, {}, {'id': 1},
            {'href': '/author/1', 'method': 'GET', 'title': ''}
        ),
        (
            '/author/<id>',
            {}, Author(1, 'William Shakespeare'), {'id': 2},
            {'href': '/author/1', 'method': 'GET', 'title': ''}
        ),
    )
)
def test_link_field_serialization(link_tpl, kwargs, obj, context, expected):
    with mock.patch.object(
        LinkField, 'context', new=mock.PropertyMock(return_value=context)
    ):
        field = LinkField(link_tpl, **kwargs)
        assert field.serialize('link', obj) == expected



