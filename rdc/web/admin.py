# -*- coding: utf-8 -*-
#
# Copyright 2012-2014 Romain Dorgueil
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from functools import partial
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.util import has_identity
from webapp2 import cached_property, abort
from wtforms.ext.sqlalchemy.orm import model_form
from rdc.web.paginator import Paginator


class View(object):
    Model = None
    route_prefix = None

    def __init__(self, **kwargs):
        self.route_prefix = kwargs.get('route_prefix', None) or self.route_prefix

    def route_for(self, action):
        if action == 'list' or action is None:
            return self.route_prefix
        return '.'.join((self.route_prefix, action, ))


class ListView(View):
    Paginator = partial(Paginator, per_page=20)
    columns = None
    actions = ['edit', 'delete']

    def __init__(self, *args, **kwargs):
        self.query = kwargs.pop('query')
        self.page = kwargs.pop('page', None)
        self.actions = kwargs.pop('actions', self.actions)

        if self.page:
            self.paginator = self.Paginator(self.query)
        else:
            self.paginator = None

        super(ListView, self).__init__(*args, **kwargs)

    def get_page(self):
        if self.paginator:
            return self.paginator.page(self.page)
        raise RuntimeError('no paginator')

    def objects(self):
        if self.paginator:
            return self.get_page().object_list
        return self.query.all()

    def __len__(self):
        return len(self.objects())

class EditView(View):
    def __init__(self, *args, **kwargs):
        self.session = kwargs.pop('session')
        self.id = kwargs.pop('id', None)

        self.form = None

        print self.session, self.id

    @property
    def query(self):
        return self.session.query(self.Model).filter(self.Model.id == self.id)

    @cached_property
    def object(self):
        if self.id:
            try:
                print self.query
                return self.query.one()
            except NoResultFound as e:
                return abort(404)

        return self.Model()

    @cached_property
    def Form(self):
        return model_form(self.Model, self.session, only=self.columns)

    def pre_commit(self):
        return True

    def commit(self):
        self.session.flush()
        self.session.commit()
        return True

    def submit(self, request, **kwargs):
        self.form = self.Form(request.POST, self.object)

        if request.method == 'POST':
            if self.form.validate():
                self.form.populate_obj(self.object)
                if self.pre_commit():
                    return self.commit()

    def object_exists(self):
        return has_identity(self.object)
