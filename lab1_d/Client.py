import asyncio
import playground
import sys
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

    def __init__(self, callback = None):
        self.buffer = ""
        if callback:
            self.callback = callback
        else:
            self.callback = print

        self.transport = None
        self.deserializer = PacketType.Deserializer()

    def close(self):
        self.__sendMessageActual("__QUIT__")

    def connection_made(self, transport):
        self.transport = transport
        #self.transport.write(self.message)
        print("Connection to JukeBox successful! \n")
        self.deserializer = PacketType.Deserializer()

    def data_received(self, data):
        self.deserializer = PacketType.Deserializer()
        self.deserializer.update(data)

        ClientRequest1 = ClientRequest()

        for pkt1 in self.deserializer.nextPackets():
            if pkt1.DEFINITION_IDENTIFIER == "ServerHello":
                #print (pkt1)
                if pkt1.AuthResponse == 1 and pkt1.GenreAvailable == 1:
                    print ("Requested genre available and authentication Suceeded! \n")
                    ClientRequest1.SessionID = pkt1.SessionID
                    ClientRequest1.ACKofServerHello = 1

                    ClientRequest1_bytes = ClientRequest1.__serialize__()
                    self.transport.write(ClientRequest1_bytes)

                elif (pkt1.AuthResponse == 0 and pkt1.GenreAvailable == 1):
                    print ("Genre is Available but auth credentials are wrong")
                    ClientRequest1.SessionID = 0
                    ClientRequest1.ACKofServerHello = 1
                    self.transport = None
                elif (pkt1.AuthResponse == 1 and pkt1.GenreAvailable == 0):
                    print("Genre is not available but auth credentials are right")
                    ClientRequest1.SessionID = 0
                    ClientRequest1.ACKofServerHello = 1
                    self.transport = None


            elif (pkt1.DEFINITION_IDENTIFIER == "ServerStream"):
                print ("Enjoy!")
                print (pkt1.Link_to_music)

            else:
                # Close connection and include new states !!!
                ClientRequest1.SessionID = 0
                ClientRequest1.ACKofServerHello = 1
                self.transport = None
    def send(self):

        packet = ClientHello(UserAuthToken = '111', Genre = 'ROCK')
        self.transport.write(packet.__serialize__())

class ControlProtocol:

    def __init__(self):
        self.txProtocol = None

    def buildProtocol(self):
        return ClientProtocol(self.callback)

    def connect(self, txProtocol):
        print ("Calling connect")
        self.txProtocol = txProtocol
        print ("Connection to Server established")
        self.txProtocol = txProtocol
        self.txProtocol.send()
        #asyncio.get_event_loop().add_reader(self.param, self.stdinAlert)

    def callback(self):
        print ("this is the message")
        sys.stdout.flush()

if __name__ == "__main__":


    loop = asyncio.get_event_loop()
    control = ControlProtocol()
    coro = playground.getConnector().create_playground_connection(control.buildProtocol, '20174.1.1.1', 102)
    transport, protocol = loop.run_until_complete(coro)
    control.connect(protocol)
    loop.run_forever()
    loop.close()

