#!/usr/bin/python3
#
# Univention Management Console
#  Univention Directory Manager Module
#
# Like what you see? Join us!
# https://www.univention.com/about-us/careers/vacancies/
#
# Copyright 2019-2023 Univention GmbH
#
# https://www.univention.de/
#
# All rights reserved.
#
# The source code of this program is made available
# under the terms of the GNU Affero General Public License version 3
# (GNU AGPL V3) as published by the Free Software Foundation.
#
# Binary versions of this program provided by Univention to you as
# well as other copyrighted, protected or trademarked materials like
# Logos, graphics, fonts, specific documentations and configurations,
# cryptographic keys etc. are subject to a license agreement between
# you and Univention and not subject to the GNU AGPL V3.
#
# In the case you use this program under the terms of the GNU AGPL V3,
# the program is provided in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License with the Debian GNU/Linux or Univention distribution in file
# /usr/share/common-licenses/AGPL-3; if not, see
# <https://www.gnu.org/licenses/>.


import argparse
import json
import logging
import os
import signal
import subprocess
import sys

import atexit
import pycurl
import tornado.httpclient
import tornado.httpserver
import tornado.httputil
import tornado.ioloop
import tornado.iostream
import tornado.process
import tornado.web
from setproctitle import getproctitle, setproctitle
from tornado.netutil import bind_sockets, bind_unix_socket

import univention.debug as ud
import univention.lib.i18n
from univention.admin.rest.shared_memory import shared_memory
from univention.management.console.config import ucr


try:
    from multiprocessing.util import _exit_function
except ImportError:
    _exit_function = None

proctitle = getproctitle()


class Gateway(tornado.web.RequestHandler):
    """
    A server which acts as proxy to multiple processes in different languages

    TODO: Implement authentication via PAM
    TODO: Implement ACL handling (restriction on certain paths for certain users/groups)
    TODO: Implement a SAML service provider
    TODO: Implement management of modules
    """

    child_id = None
    PROCESSES = {}
    SOCKETS = {}

    def set_default_headers(self):
        self.set_header('Server', 'Univention/1.0')  # TODO:

    @tornado.gen.coroutine
    def get(self):
        try:
            accepted_language, language_socket = self.select_language()
        except univention.lib.i18n.I18N_Error:
            accepted_language, language_socket = None, None
        if language_socket is None:  # pragma: no cover
            raise tornado.web.HTTPError(406)

        request = tornado.httpclient.HTTPRequest(
            self.request.full_url(),
            method=self.request.method,
            body=self.request.body or None,
            headers=self.request.headers,
            allow_nonstandard_methods=True,
            follow_redirects=False,
            connect_timeout=20.0,  # TODO: raise value?
            request_timeout=int(ucr.get('directory/manager/rest/response-timeout', '310')) + 1,
            prepare_curl_callback=lambda curl: curl.setopt(pycurl.UNIX_SOCKET_PATH, language_socket),
        )
        client = tornado.httpclient.AsyncHTTPClient()
        try:
            response = yield client.fetch(request, raise_error=True)
        except tornado.curl_httpclient.CurlError as exc:
            ud.debug(ud.MAIN, ud.WARN, f'Reaching service failed: {exc}')
            # happens during starting the service and subprocesses when the UNIX sockets aren't available yet
            self.set_status(503)
            self.add_header('Retry-After', '3')  # Tell clients, we are ready in 3 seconds
            self.add_header('Content-Type', 'application/json')
            self.write(json.dumps('The service could not be reached. Please retry in a few seconds or contact an Administrator to restart the service.'))
            self.finish()
            return
        except tornado.httpclient.HTTPError as exc:
            response = exc.response

        self.set_status(response.code, response.reason)
        self._headers = tornado.httputil.HTTPHeaders()

        self.add_header('Content-Language', accepted_language)
        for header, v in response.headers.get_all():
            if header not in ('Content-Length', 'Transfer-Encoding', 'Content-Encoding', 'Connection', 'X-Http-Reason'):
                self.add_header(header, v)

        if response.body:
            self.set_header('Content-Length', len(response.body))
            self.write(response.body)
        self.finish()

    post = put = delete = patch = options = get

    def select_language(self):
        languages = self.request.headers.get("Accept-Language", "en-US").split(",")
        locales = []
        defaults = {'en_US': 0.01, 'de_DE': 0.02}
        for language in languages:
            parts = language.strip().split(";")
            if len(parts) > 1 and parts[1].strip().startswith("q="):
                try:
                    quality = float(parts[1].strip()[2:])
                except (ValueError, TypeError):
                    quality = 0.0
            else:
                quality = 1.0
            defaults.pop(parts[0], None)
            if quality > 0:
                locales.append((parts[0], quality))
        locales = [lang[0].replace('-', '_') for lang in sorted(locales + list(defaults.items()), key=lambda x: x[1], reverse=True)]

        for locale in locales + ['en_US', 'de_DE']:
            locale = '%s_%s' % self.get_locale(locale)
            if locale in self.SOCKETS:
                return locale.replace('_', '-'), self.SOCKETS[locale]
        return 'C', None

    @classmethod
    def main(cls):
        parser = argparse.ArgumentParser(prog=f'{sys.executable} -m univention.admin.rest.server')
        parser.add_argument('-d', '--debug', type=int, default=ucr.get_int('directory/manager/rest/debug/level', 2))
        parser.add_argument('-p', '--port', help='Bind to a TCP port (%(default)s)', type=int, default=ucr.get_int('directory/manager/rest/server/port'))
        parser.add_argument('-i', '--interface', help='Bind to specified interface address (%(default)s)', default=ucr['directory/manager/rest/server/address'])
        parser.add_argument('-s', '--unix-socket', help='Bind to specified UNIX socket')
        parser.add_argument('-c', '--processes', type=int, default=ucr.get_int('directory/manager/rest/processes'), help='How many processes should be forked')
        args = parser.parse_args()

        setproctitle(proctitle + '   # gateway main')
        ud.init('stdout', ud.FLUSH, ud.NO_FUNCTION)
        ud.set_level(ud.MAIN, args.debug)

        tornado.httpclient.AsyncHTTPClient.configure('tornado.curl_httpclient.CurlAsyncHTTPClient')
        tornado.locale.load_gettext_translations('/usr/share/locale', 'univention-management-console-module-udm')

        os.umask(0o077)  # FIXME: should probably be changed, this is what UMC sets

        channel = logging.StreamHandler()
        channel.setFormatter(tornado.log.LogFormatter(fmt='%(color)s%(asctime)s  %(levelname)10s      (%(process)9d) :%(end_color)s %(message)s', datefmt='%d.%m.%y %H:%M:%S'))
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(channel)

        # bind sockets
        socks = []
        if args.port:
            socks.extend(bind_sockets(args.port, args.interface, reuse_port=True))
        if args.unix_socket:
            socks.append(bind_unix_socket(args.unix_socket))

        # start sharing memory (before fork, before first usage, after import)
        shared_memory.start()

        # start sub processes for each required locale
        try:
            cls.start_processes(args.processes, args.port, args.debug)
        except Exception:
            cls.signal_handler_stop(signal.SIGTERM, None)
            raise

        cls.register_signal_handlers()

        # start mutliprocessing
        if args.processes != 1:
            if _exit_function is not None:
                atexit.unregister(_exit_function)
            cls.socks = socks
            try:
                child_id = tornado.process.fork_processes(args.processes, 0)
            except RuntimeError as exc:
                logger.info(f'Stopped process {exc}')
                cls.signal_handler_stop(signal.SIGTERM, None)
            else:
                cls.start_child(child_id)
        else:
            cls.start_server(socks)

    @classmethod
    def start_child(cls, child_id):
        setproctitle(proctitle + f'   # gateway proxy {child_id}')
        cls.child_id = child_id
        logger = logging.getLogger()
        logger.info('Started child %s', cls.child_id)
        shared_memory.children[cls.child_id] = os.getpid()
        cls.start_server(cls.socks)

    @classmethod
    def start_server(cls, socks):
        app = tornado.web.Application([
            (r'.*', cls),
        ], serve_traceback=ucr.is_true('directory/manager/rest/show-tracebacks', True),
        )
        server = tornado.httpserver.HTTPServer(app)
        server.add_sockets(socks)

        try:
            tornado.ioloop.IOLoop.current().start()
        except Exception:
            cls.signal_handler_stop(signal.SIGTERM, None)
            raise

    @classmethod
    def get_locale(cls, language):
        locale = univention.lib.i18n.Locale(language)
        territory = locale.territory or {'de': 'DE', 'en': 'US'}.get(locale.language)
        return locale.language, territory

    @classmethod
    def get_socket_for_locale(cls, language):
        language, territory = cls.get_locale(language)
        return f'/var/run/univention-directory-manager-rest-{language}-{territory.lower()}.socket'

    @classmethod
    def start_processes(cls, num_processes=1, start_port=9979, debug_level=2):
        languages = [
            language.split(':', 1)[0]
            for language in ucr.get('locale', 'de_DE.UTF-8:UTF-8 en_US.UTF-8:UTF-8').split()
        ]
        for language in languages:
            cmd = [sys.executable, '-m', 'univention.admin.rest', '-l', language, '-c', str(num_processes), '-d', str(debug_level)]
            language = language.split('.', 1)[0]

            sock = cls.get_socket_for_locale(language)
            cmd.extend(['-s', sock])

            short_lang = language.split('_', 1)[0]
            cls.SOCKETS[language] = cls.SOCKETS.get(short_lang, sock)
            if short_lang in cls.SOCKETS:
                continue
            cls.SOCKETS[short_lang] = sock
            cls.PROCESSES[language] = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)

    @classmethod
    def register_signal_handlers(cls):
        signal.signal(signal.SIGTERM, cls.signal_handler_stop)
        signal.signal(signal.SIGINT, cls.signal_handler_stop)
        signal.signal(signal.SIGHUP, cls.signal_handler_reload)

    @classmethod
    def signal_handler_reload(cls, sig, frame):
        if cls.child_id is None:
            for process in cls.PROCESSES.values():
                cls.safe_kill(process.pid, sig)

    @classmethod
    def signal_handler_stop(cls, sig, frame):
        logger = logging.getLogger()
        if cls.child_id is None:
            try:
                children_pids = list(shared_memory.children.values())
            except Exception:  # multiprocessing failure
                children_pids = []
            logger.info('stopping children: %r', children_pids)
            for pid in children_pids:
                cls.safe_kill(pid, sig)
            logger.info('stopping subprocesses: %r', list(cls.PROCESSES.keys()))
            for process in cls.PROCESSES.values():
                cls.safe_kill(process.pid, sig)

            shared_memory.shutdown()
        else:
            logger.info('shutting down')

        io_loop = tornado.ioloop.IOLoop.current()

        def shutdown():
            io_loop.stop()

        io_loop.add_callback_from_signal(shutdown)

    @classmethod
    def safe_kill(cls, pid, signo):
        try:
            os.kill(pid, signo)
        except OSError as exc:
            logging.getLogger().error(f'Could not kill({signo}) {pid}: {exc}')
        else:
            os.waitpid(pid, os.WNOHANG)
