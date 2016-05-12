#!/usr/bin/env python
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2016-05-10 11:26:49 +0100 (Tue, 10 May 2016)
#
#  https://github.com/harisekhon/pytools
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn
#  and optionally send me feedback to help improve this or other code I publish
#
#  https://www.linkedin.com/in/harisekhon
#

"""

Tool to show Docker tags for one or more DockerHub repos

Written for convenience as Docker CLI doesn't currently support this:

See https://github.com/docker/docker/issues/17238

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals

import json
import logging
import os
import sys
import traceback
import urllib
try:
    import requests
except ImportError:
    print(traceback.format_exc(), end='')
    sys.exit(4)
srcdir = os.path.abspath(os.path.dirname(__file__))
libdir = os.path.join(srcdir, 'pylib')
sys.path.append(libdir)
try:
    # pylint: disable=wrong-import-position
    from harisekhon.utils import log, die, prog, isJson, jsonpp
    from harisekhon import CLI
except ImportError as _:
    print(traceback.format_exc(), end='')
    sys.exit(4)

__author__ = 'Hari Sekhon'
__version__ = '0.2'


class DockerHubTags(CLI):

    def __init__(self):
        # Python 2.x
        super(DockerHubTags, self).__init__()
        # Python 3.x
        # super().__init__()
        self._CLI__parser.usage = '{0} [options] repo1 repo2 ...'.format(prog)

    def run(self):
        if not self.args:
            self.usage('no repos given as args')
        print('DockerHub\n')
        for arg in self.args:
            self.print_tags(arg)

    def print_tags(self, repo):
        print('repo: {0}'.format(repo))
        print('tags: ', end='')
        sys.stdout.flush()
        print('\n      '.join(self.get_tags(repo)) + '\n')

    @staticmethod
    def get_tags(repo):
        namespace = 'library'
        if '/' in repo:
            (namespace, repo) = repo.split('/', 2)
        url = 'https://registry.hub.docker.com/v2/repositories/{0}/{1}/tags/'.format(urllib.quote_plus(namespace), urllib.quote_plus(repo))
        log.debug('GET %s' % url)
        try:
            # workaround for Travis CI and older pythons - we're not exchanging secret data so this is ok
            verify = True
            if os.getenv('TRAVIS'):
                verify = False
            req = requests.get(url, verify=verify)
        except requests.exceptions.RequestException as _:
            die(_)
        log.debug("response: %s %s", req.status_code, req.reason)
        log.debug("content:\n%s\n%s\n%s", '='*80, req.content.strip(), '='*80)
        if req.status_code != 200:
            die("%s %s" % (req.status_code, req.reason))
        if not isJson(req.content):
            die('invalid non-JSON response from DockerHub!')
        if log.isEnabledFor(logging.DEBUG):
            print(jsonpp(req.content))
            print('='*80)
        tag_list = []
        try:
            j = json.loads(req.content)
            tag_list = [_['name'] for _ in j['results']]
        except KeyError as _:
            die('failed to parse output from DockerHub (format may have changed?): {0}'.format(_))
        tag_list.sort()
        # put latest to the top of the list
        try:
            tag_list.insert(0, tag_list.pop(tag_list.index('latest')))
        except ValueError:
            pass
        return tag_list


if __name__ == '__main__':
    DockerHubTags().main()
