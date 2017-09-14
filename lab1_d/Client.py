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

class ClientProtocol(asyncio.Protocol):

    def __init__(self, message, loop):
        #self.ipaddress = '127.0.0.1'
        #self.port = 16000
        self._transport =  None
        self.message = message.__serialize__()
        self.loop = loop

    def connection_made(self, transport):
        self._transport = transport
        self._transport.write(self.message)
        print("Connection to JukeBox successful! \n")
        self._deserializer = PacketType.Deserializer()

    def data_received(self, data):
        self._deserializer = PacketType.Deserializer()
        self._deserializer.update(data)

        ClientRequest1 = ClientRequest()

        for pkt1 in self._deserializer.nextPackets():
            if pkt1.DEFINITION_IDENTIFIER == "ServerHello":
                #print (pkt1)
                if pkt1.AuthResponse == 1 and pkt1.GenreAvailable == 1:
                    print ("Requested genre available and authentication Suceeded! \n")
                    ClientRequest1.SessionID = pkt1.SessionID
                    #print (pkt1.SessionID)
                    #dict[pkt1.SessionID] = "Server_Hello_Rcd"
                    ClientRequest1.ACKofServerHello = 1

                    ClientRequest1_bytes = ClientRequest1.__serialize__()
                    self._transport.write(ClientRequest1_bytes)

                elif (pkt1.AuthResponse == 0 and pkt1.GenreAvailable == 1):
                    print ("Genre is Available but auth credentials are wrong")
                    ClientRequest1.SessionID = 0
                    ClientRequest1.ACKofServerHello = 1
                    self._transport = None
                elif (pkt1.AuthResponse == 1 and pkt1.GenreAvailable == 0):
                    print("Genre is not available but auth credentials are right")
                    ClientRequest1.SessionID = 0
                    ClientRequest1.ACKofServerHello = 1
                    self._transport = None


            elif (pkt1.DEFINITION_IDENTIFIER == "ServerStream"):
                print ("Enjoy!")
                print (pkt1.Link_to_music)

            else:
                # Close connection and include new states !!!
                ClientRequest1.SessionID = 0
                ClientRequest1.ACKofServerHello = 1
                self._transport = None
                #print ("Unexpected Error!")




loop = asyncio.get_event_loop()

ClientHello1 = ClientHello()
ClientHello1.UserAuthToken = '111'
ClientHello1.Genre = 'POP'

message = ClientHello1

playground.getConnector().create_playground_connection (lambda: ClientProtocol(message, loop), '20174.1.1.1', 101)

loop.run_until_complete()

#loop.run_forever()
loop.close()
