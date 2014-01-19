# -*- coding: utf-8 -*-
#
# Author: Romain Dorgueil <romain@dorgueil.net>
# Copyright: © 2011-2013 SARL Romain Dorgueil Conseil
#

from webapp2 import cached_property


class Entry(object):
    def __init__(self, title, route=None):
        self.title = title
        self.route = route
        self.parent = None
        self.children = [ ]

    def add_children(self, *args):
        for arg in args:
            if not arg.parent:
                arg.parent = self
            self.children.append(arg)
        return self

    def generate_url_with(self, uri_for):
        if self.route:
            return uri_for(self.route)
        else:
            return '#'

    def get_path(self):
        e, path = self, [self]
        while e.parent:
            path.append(e.parent)
            e = e.parent
        return reversed(path)

    def get_root(self):
        e = self
        while e.parent: e = e.parent
        return e

    def __unicode__(self):
        return self.title

    def __repr__(self):
        return '<{0} title="{1}" route="{2}">'.format(type(self).__name__, self.title, self.route)

class Root(Entry):
    def __init__(self, title, route=None):
        super(Root, self).__init__(title, route)

    @cached_property
    def index(self):
        def _index(entry):
            return [(entry.route, entry)] + reduce(lambda a, b: a + b, [_index(child) for child in entry.children], [])
        return dict(_index(self))

    def get_index(self):
        return self.index
