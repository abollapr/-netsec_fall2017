import asyncio
import playground
from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import UINT32,STRING,BOOL,ListFieldType
from playground.asyncio_lib.testing import TestLoopEx
from playground.network.testing import MockTransportToStorageStream
from playground.network.testing import MockTransportToProtocol
import re
import random
#from playground.common import logging as p_logging
#p_logging.EnablePresetLogging(p_logging.PRESET_TEST)

#ClientHello Packet
class ClientHello(PacketType):
    DEFINITION_IDENTIFIER = "ClientHello"
    DEFINITION_VERSION = "1.0"

    FIELDS = [
        ("UserAuthToken", UINT32),
        ("Genre", STRING)
        ]

#ServerHello Packet
class ServerHello(PacketType):
    DEFINITION_IDENTIFIER = "ServerHello"
    DEFINITION_VERSION = "1.0"

    FIELDS = [
        ("SessionID", UINT32),
        ("AuthResponse", BOOL),
        ("GenreAvailable", BOOL)
        #("RequestBitRate", STRING)
    ]

#ClientRequest Packet
class ClientRequest(PacketType):
    DEFINITION_IDENTIFIER = "ClientRequest"
    DEFINITION_VERSION = "1.0"

    FIELDS = [
        ("SessionID", UINT32),
        ("ACKofServerHello",  BOOL)
        #("BitRate", ListFieldType(STRING))
    ]

#ServerStream Packet
class  ServerStream(PacketType):
    DEFINITION_IDENTIFIER = "ServerStream"
    DEFINITION_VERSION = "1.0"

    FIELDS = [
        ("SessionID", UINT32),
        ("Link_to_music", STRING)
    ]

###########################

class ServerProtocol(asyncio.Protocol):

    def __init__(self):
        #self._ip_address = '127.0.0.1'
        #self._port = 8000
        self._transport = None
        self.GenreList = ["ROCK", "POP", "CLASSICAL", "JAZZ"]


    def connection_made(self, transport):
        self._transport = transport
        print ("Welcome to The Jukebox! \n")
        self._deserializer = PacketType.Deserializer()
        self._session_ID = random.randint(1,100)


    def Packet2Bytes(self, pkt):

        ServerHello1 = ServerHello()

        ServerHello1.SessionID = self._session_ID

        if re.match("^\d\d\d$", str(pkt.UserAuthToken)):
            ServerHello1.AuthResponse = 1
            if pkt.Genre in self.GenreList:
                ServerHello1.GenreAvailable = 1
            else:
                ServerHello1.GenreAvailable = 0
        else:
            ServerHello1.AuthResponse = 0
            if pkt.Genre in self.GenreList:
                ServerHello1.GenreAvailable = 1
            else:
                ServerHello1.GenreAvailable = 0
            print (ServerHello1.SessionID)

        self.ServerHello_bytes = ServerHello1.__serialize__()
        self._transport.write(self.ServerHello_bytes)


    def Packet2Bytes1(self, pkt, genre_requested_c):

        ServerStream1 = ServerStream()

        ServerStream1.SessionID = pkt.SessionID

        self.genre_requested_c = genre_requested_c

        if self.genre_requested_c == "ROCK":
            print ("Let's Rock!")
            ServerStream1.Link_to_music = "https://www.youtube.com/watch?v=3_5RbI9goz4"
        elif self.genre_requested_c == "POP":
            ServerStream1.Link_to_music = "https://www.youtube.com/watch?v=2VncTzuXhu0&list=PLMAV5w57ey1rYKkjhUwVpdLn3wCUTurGC"
        elif self.genre_requested_c == "CLASSICAL":
            ServerStream1.Link_to_music = "https://www.youtube.com/watch?v=a-b6JgQa3EY&list=PLauX1OLju8VgJ1-oBaBDGKZeAiFav-mAE"
        elif self.genre_requested_c == "JAZZ":
            ServerStream1.Link_to_music = "https://www.youtube.com/watch?v=2o4NyCE8-Zs&list=PLjBo9Ev93QFXo9_14jtlHGEir4G_omx34"
        else:
            ServerStream1.Link_to_music == "Unexpected error"

        self.ServerStream_bytes = ServerStream1.__serialize__()
        self._transport.write(self.ServerStream_bytes)


    def data_received(self, data):
        self._deserializer = PacketType.Deserializer()
        self._deserializer.update(data)

        for pkt in self._deserializer.nextPackets():
            if (pkt.DEFINITION_IDENTIFIER == "ClientHello"):
                #dict[self._session_ID] = "Server_Hello_State"
                self.return_value = self.Genre_Requested_by_Client_function(pkt.Genre)
                self.Packet2Bytes(pkt)
            elif (pkt.DEFINITION_IDENTIFIER == "ClientRequest"):
                #dict[self._session_ID] = "Server_Stream_State"
                self.Packet2Bytes1(pkt, self.return_value)

    def Genre_Requested_by_Client_function(self, genre_req):
        return genre_req

    def connection_lost(self, exc):
        self._transport = None


loop = asyncio.get_event_loop()
coro = playground.getConnector().create_playground_server(lambda: ServerProtocol, 101)
server = loop.run_until_complete(coro)
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

server.close()
loop.close()


