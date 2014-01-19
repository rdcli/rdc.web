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

import os
from webapp2 import RequestHandler as BaseRequestHandler, cached_property, Response, abort
from webapp2_extras import jinja2
from webob.static import FileApp


class RequestHandler(BaseRequestHandler):
    def get_service(self, name):
        """Use service container aware application to retrieve a service instance."""
        return self.app.container.get(name)

    @cached_property
    def jinja2(self):
        """ xxx todo """
        j = jinja2.get_jinja2(app=self.app)
        # not good.
        j.environment.globals.update({
            'uri_for': self.uri_for,
            })
        return j

    def render_response(self, _template, **context):
        """Renders a template and writes the result to the response."""
        self.response.write(self.jinja2.render_template(_template, **context))

def StaticFileHandler(base_path):
    def handler(request, *args, **kwargs):
        abs_path = os.path.join(base_path, kwargs.get('path'))
        if os.path.isdir(abs_path) or abs_path.find(os.getcwd()) != 0:
            return abort(403)
        try:
            file = FileApp(abs_path)
            return file.__call__.func(request)
        except:
            return abort(404)

    handler.__name__ = StaticFileHandler.__name__
    return handler

