# encoding: utf-8
"""
listen.py

Created by Thomas Mangin on 2013-07-11.
Copyright (c) 2013-2013 Exa Networks. All rights reserved.
"""

import socket

from exabgp.util.errstr import errstr

from exabgp.protocol.family import AFI
from exabgp.protocol.ip import IP

#from exabgp.util.coroutine import each

from exabgp.reactor.network.tcp import create
from exabgp.reactor.network.tcp import bind
from exabgp.reactor.network.tcp import async
from exabgp.reactor.network.tcp import keepalive

from exabgp.reactor.network.error import error
from exabgp.reactor.network.error import errno
from exabgp.reactor.network.error import NetworkError
from exabgp.reactor.network.error import BindingError
from exabgp.reactor.network.error import AcceptError
from exabgp.reactor.network.incoming import Incoming

from exabgp.logger import Logger
from exabgp.configuration.environment import environment


class Listener (object):
	def __init__ (self,hosts,port,backlog=200):
		self._hosts = hosts
		self._port = port
		self._backlog = backlog

		self.serving = False
		self._sockets = {}
		#self._connected = {}
		self.logger = Logger()

		self.keepalive = environment.settings().tcp.keepalive

	def _bind (self,ip,port):
		s = create(IP.toafi(ip))
		bind(s,ip)
		async(s,ip)

		if self.keepalive:
			keepalive(s,ip)

		try:
			s.listen(self._backlog)
			return s
		except socket.error, e:
			if e.args[0] == errno.EADDRINUSE:
				raise BindingError('could not listen on %s:%d, the port already in use by another application' % (ip,self._port))
			elif e.args[0] == errno.EADDRNOTAVAIL:
				raise BindingError('could not listen on %s:%d, this is an invalid address' % (ip,self._port))
			else:
				raise BindingError('could not listen on %s:%d (%s)' % (ip,self._port,errstr(e)))

	def start (self):
		try:
			for host in self._hosts:
				if (host,self._port) not in self._sockets:
					s = self._bind(host,self._port)
					self._sockets[s] = (host,self._port)
			self.serving = True
		except NetworkError,e:
				self.logger.network(str(e),'critical')
				raise e
		self.serving = True

	# @each
	def connected (self):
		if not self.serving:
			return

		try:
			for sock,(host,_) in self._sockets.items():
				try:
					io, _ = sock.accept()
					local_ip,local_port = io.getpeername()
					remote_ip,remote_port = io.getsockname()
					yield Incoming(AFI.ipv4,remote_ip,local_ip,io)
					break
				except socket.error, e:
					if e.errno in error.block:
						continue
					raise AcceptError('could not accept a new connection (%s)' % errstr(e))
		except NetworkError,e:
			self.logger.network(str(e),'critical')
			raise e

	def stop (self):
		if not self.serving:
			return

		for sock,(ip,port) in self._sockets.items():
			sock.close()
			self.logger.network('stopped listening on %s:%d' % (ip,port),'info')

		self._sockets = {}
		self.serving = False
