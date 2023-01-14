import time
import threading
from common import *

GRAPH_ID = "effects"

class testEffects():
    async def wait_for_command(self):
        monitor_response = await self.monitor.next_command()
        return monitor_response
    
    def monitor_thread(self):
        with self.replica.monitor() as m:
            for cmd in m.listen():
                if 'GRAPH.EFFECT' in cmd['command']:
                    self.commands.append(cmd['command'][len('GRAPH.EFFECT ' + GRAPH_ID):])

    def __init__(self):
        self.env = Env(decodeResponses=True, env='oss', useSlaves=True)
        self.master = self.env.getConnection()
        self.replica = self.env.getSlaveConnection()
        self.master_graph = Graph(self.master, GRAPH_ID)
        self.replica_graph = Graph(self.replica, GRAPH_ID)
        self.commands = []

        monitor_thread = threading.Thread(target=self.monitor_thread)
        monitor_thread.start()
    
    def test01_add_schema_effect(self):
        # test the introduction of a schema by an effect

        # introduce a new label which in turn creates a new schema
        q = "CREATE (:L)"
        self.master_graph.query(q)

        # wait for monitor to receive commands
        while len(self.commands) != 1:
            time.sleep(1)

        # TODO: validate effect
        cmd = self.commands.pop()

        q = "MATCH (n:L) RETURN n"
        master_resultset = self.master_graph.query(q).result_set
        replica_resultset = self.replica_graph.query(q, read_only=True).result_set
        self.env.assertEquals(master_resultset, replica_resultset)

    def test02_add_attribute_effect(self):
        # test the introduction of an attribute by an effect

        # introduce a new label which in turn creates a new schema
        q = "MATCH (n:L) SET n.a = 1, n.b = 'str', n.c = True, n.d = [1, [2], '3'], n.e = point({latitude: 51, longitude: 0}), n.f=3.14"
        # TODO: support string
        q = "MATCH (n:L) SET n.a = 1, n.c = True, n.d = [1, [2]], n.e = point({latitude: 51, longitude: 0}), n.f=3.14"

        self.master_graph.query(q)

        # wait for monitor to receive commands
        while len(self.commands) != 1:
            time.sleep(1)

        # TODO: validate effect
        cmd = self.commands.pop()

        q = "MATCH (n:L) RETURN n"
        master_resultset = self.master_graph.query(q).result_set
        replica_resultset = self.replica_graph.query(q, read_only=True).result_set
        self.env.assertEquals(master_resultset, replica_resultset)

    def test03_create_node_effect(self):
        # test the introduction of a new node by an effect
        q = "CREATE (:L {a:1, b:'str', c:True, d:[1, [2], '3'], e:point({latitude: 51, longitude: 0}), f:3.14})"
        #TODO: support string
        q = "CREATE (:L {a:1, c:True, d:[1, [2]], e:point({latitude: 51, longitude: 0}), f:3.14})"
        self.master_graph.query(q)

        # wait for monitor to receive commands
        while len(self.commands) != 1:
            time.sleep(1)

        # TODO: validate effect
        cmd = self.commands.pop()

        q = "MATCH (n) RETURN n ORDER BY n"
        master_resultset = self.master_graph.query(q).result_set
        replica_resultset = self.replica_graph.query(q, read_only=True).result_set
        self.env.assertEquals(master_resultset, replica_resultset)

    def test04_update_effect(self):
        # test an entity attribute set update by an effect
        q = "MATCH (n:L) WITH n LIMIT 1 SET n.a = 2, n.b = 'string', n.c = False, n.d = [[2], 1, '3'], n.e = point({latitude: 41, longitude: 2}), n.f=6.28"
        #TODO: support string
        q = "MATCH (n:L) WITH n LIMIT 1 SET n.a = 2, n.c = False, n.d = [[2], 1], n.e = point({latitude: 41, longitude: 2}), n.f=6.28"

        self.master_graph.query(q)

        # wait for monitor to receive commands
        while len(self.commands) != 1:
            time.sleep(1)

        # TODO: validate effect
        cmd = self.commands.pop()

        q = "MATCH (n) RETURN n ORDER BY n"
        master_resultset = self.master_graph.query(q).result_set
        replica_resultset = self.replica_graph.query(q, read_only=True).result_set
        self.env.assertEquals(master_resultset, replica_resultset)

    def test05_set_labels_effect(self):
        # test the addition of a new node label by an effect
        pass

    def test06_remove_labels_effect(self):
        # test the removal of a node label by an effect
        pass

    def test07_create_edge_effect(self):
        # tests the introduction of a new edge by an effect
        pass

    def test08_delete_edge_effect(self):
        # test the deletion of an edge by an effect
        pass

    def test09_delete_node_effect(self):
        # test the deletion of a node by an effect
        q = "MATCH (n) DELETE n"
        self.master_graph.query(q)

        # wait for monitor to receive commands
        while len(self.commands) != 1:
            time.sleep(1)

        # TODO: validate effect
        cmd = self.commands.pop()

        q = "MATCH (n) RETURN count(n)"
        master_resultset = self.master_graph.query(q).result_set
        replica_resultset = self.replica_graph.query(q, read_only=True).result_set
        self.env.assertEquals(master_resultset, replica_resultset)

