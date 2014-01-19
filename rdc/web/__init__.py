# -*- coding: utf-8 -*-
#
# Author: Romain Dorgueil <romain@dorgueil.net>
# Copyright: © 2011-2013 SARL Romain Dorgueil Conseil
#

from webapp2 import WSGIApplication

class Application(WSGIApplication):
    def __init__(self, container, routes=None, debug=False, config=None):
        super(Application, self).__init__(routes, debug, config)
        self.container = container
        self.get_service = container.get

    def _internal_error(self, exception):
        if self.debug:
            raise
        return super(Application, self)._internal_error(exception)
