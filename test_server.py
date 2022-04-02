import socket
import unittest

from server import Server


class TestServerBadNickname(unittest.TestCase):
    def setUp(self):
        self.server = Server()
    def test_badnickname_true(self):
        self.server.nicknames.add('foo')
        self.assertTrue(self.server.bad_nickname('foo'))
    def test_badnickname_false(self):
        self.assertFalse(self.server.bad_nickname('bar'))
    def test_badnickname_add_name(self):
        self.assertFalse(self.server.bad_nickname('bar'))
        self.assertTrue(self.server.bad_nickname('bar'))
    def test_badnickname_send_accept(self):
        pass
    def test_badnickname_send_reject(self):
        pass
    def tearDown(self):
        self.server.server.close()


class TestServerInitializer(unittest.TestCase):
    def setUp(self):
        self.server = Server()
    def test_init_port(self):
        self.assertEqual(self.server.PORT, 5050)
    def test_init_ip(self):
        self.assertEqual(self.server.SERVER,('127.0.0.1'or'10.0.0.179'))
    def test_init_addr(self):
        self.assertEqual(self.server.ADDR, ('127.0.0.1'or'10.0.0.179', 5050))
    def test_init_server(self):
        self.assertIsInstance(self.server.server,socket.socket)
    def test_init_nicknames_empty(self):
        self.assertEqual(self.server.nicknames, set())
    def test_init_clients_empty(self):
        self.assertEqual(self.server.clients, set())
    def tearDown(self):
        self.server.server.close()


class TestServerSetUp(unittest.TestCase):
    def setUp(self):
        self.server = Server()

    def test_setup(self):
        pass

    def tearDown(self):
        self.server.server.close()


if __name__ == '__main__':
    unittest.main()