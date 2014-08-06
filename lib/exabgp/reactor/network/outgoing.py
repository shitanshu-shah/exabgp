from exabgp.reactor.network.connection import Connection
from exabgp.reactor.network.tcp import create,bind
from exabgp.reactor.network.tcp import connect
from exabgp.reactor.network.tcp import MD5
from exabgp.reactor.network.tcp import nagle
from exabgp.reactor.network.tcp import TTL
from exabgp.reactor.network.tcp import async
from exabgp.reactor.network.tcp import keepalive
from exabgp.reactor.network.tcp import ready
from exabgp.reactor.network.error import NetworkError

from exabgp.configuration.environment import environment

class Outgoing (Connection):
	direction = 'outgoing'

	def __init__ (self,afi,peer,local,port=179,md5='',ttl=None):
		Connection.__init__(self,afi,peer,local)

		self.logger.wire("Attempting connection to %s" % self.peer)

		self.peer = peer
		self.ttl = ttl
		self.afi = afi
		self.md5 = md5
		self.port = port
		self.keepalive = environment.settings().tcp.keepalive

		try:
			self.io = create(afi)
			MD5(self.io,peer,port,afi,md5)
			bind(self.io,local,afi)
			async(self.io,peer)
			if self.keepalive:
				keepalive(self.io,peer)
			connect(self.io,peer,port,afi,md5)
			self.init = True
		except NetworkError,e:
			self.init = False
			self.close()
			self.logger.wire("Connection failed, %s" % str(e))

	def establish (self):
		if not self.init:
			yield False
			return

		try:
			generator = ready(self.io)
			while True:
				connected = generator.next()
				if not connected:
					yield False
					continue
				yield True
				return
		except StopIteration:
			# self.io MUST NOT be closed here, it is closed by the caller
			yield False
			return

		nagle(self.io,self.peer)
		TTL(self.io,self.peer,self.ttl)
		yield True
