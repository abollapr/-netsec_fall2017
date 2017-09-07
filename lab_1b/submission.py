from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import UINT32,STRING,BOOL,ListFieldType
import random
import re

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
        ("GenreAvailable", BOOL),
        ("RequestBitRate", STRING)
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
        ("Linktomusic", STRING)
    ]


def basicUnitTest():

    print ("~~~Welcome to Jukebox!~~~")

    Genre = input("Please Enter the genre you would like to listen to! Available options - Rock/Pop/Classical/Jazz \n")
    Genre = Genre.upper()
    print (Genre)
    AuthToken = input("Enter your authentication token - 3 digit\n")

    if int(AuthToken)>0:

        ClientHello1 = ClientHello()
        ClientHello1.UserAuthToken = AuthToken
        ClientHello1.Genre = str(Genre)

        #Sending the packet
        packetBytes = ClientHello1.__serialize__()
        deserializer_ClientHello = PacketType.Deserialize(packetBytes)

        if deserializer_ClientHello == ClientHello1:
            print ("\nClient Hello has been successfully serialized and deserialized \n")
        else:
            print ("\nHouston, we have a problem! \n")
            return

        #Genres
        GenreList = ["ROCK","POP","CLASSICAL","JAZZ"]
        #AuthTokens
        #UserTokens = [123,345,567,789,901]

        print ("==Server processing Client Hello==")

        #Generating Random Session IDs
        SessionID_Random = random.randint(1,100)

        ServerHello1 = ServerHello()
        ServerHello1.SessionID = SessionID_Random

        #Keeping track of all ongoing sessions
        #SessionID_Random_List = []
        #SessionID_Random_List.insert(0,SessionID_Random)

        if re.match("^\d\d\d$", str(deserializer_ClientHello.UserAuthToken)):

            ServerHello1.AuthResponse = 1
            ServerHello1.RequestBitRate = "Enter the bit rate at which you would like to listen to your music"

            if deserializer_ClientHello.Genre in GenreList:
                ServerHello1.GenreAvailable = 1
            else:
                ServerHello1.GenreAvailable = 0
        else:
            ServerHello1.AuthResponse =0
            ServerHello1.GenreAvailable = 0
            ServerHello1.RequestBitRate = "NULL"

        #Sending out the Server response
        packetBytes1 = ServerHello1.__serialize__()

        deserializer1 = PacketType.Deserialize(packetBytes1)

        if (deserializer1.GenreAvailable == True and deserializer1.AuthResponse == 1):
            print ("Your requested Genre is available!")
        else:
            print ("SERVER SIDE ERROR: Error with Genre or Username")

        ClientRequest1 = ClientRequest()
        ClientRequest1.SessionID = deserializer1.SessionID
        #print (ClientRequest1.SessionID)
        ClientRequest1.ACKofServerHello = 1
        if (deserializer1.AuthResponse == 1 and deserializer1.GenreAvailable == 1):
            print ("Authentication Succeeded")
            #ClientRequest1.BitRate = ["320Kbps","123Kbps"]
        else:
            print ("Authentication Failed :( ")
            #ClientRequest1.BitRate = ["0"]
            return (basicUnitTest())

        ClientRequest1_serialize = ClientRequest1.__serialize__()

        ClientRequest1_deserailze = PacketType.Deserialize(ClientRequest1_serialize)

        assert ClientRequest1_deserailze == ClientRequest1

        ServerStream1 = ServerStream()
        ServerStream1.SessionID = deserializer1.SessionID

        if deserializer_ClientHello.Genre == "ROCK":
            ServerStream1.Linktomusic = "https://www.youtube.com/watch?v=3_5RbI9goz4"
        elif deserializer_ClientHello.Genre == "POP":
            ServerStream1.Linktomusic = "https://www.youtube.com/watch?v=2VncTzuXhu0&list=PLMAV5w57ey1rYKkjhUwVpdLn3wCUTurGC"
        elif deserializer_ClientHello.Genre == "CLASSICAL":
            ServerStream1.Linktomusic = "https://www.youtube.com/watch?v=a-b6JgQa3EY&list=PLauX1OLju8VgJ1-oBaBDGKZeAiFav-mAE"
        elif deserializer_ClientHello.Genre == "JAZZ":
            ServerStream1.Linktomusic = "https://www.youtube.com/watch?v=2o4NyCE8-Zs&list=PLjBo9Ev93QFXo9_14jtlHGEir4G_omx34"
        else:
            ServerStream1.Linktomusic == "Unexpected error"

        ServerStream1_serializer = ServerStream1.__serialize__()

        deserializer1 =  PacketType.Deserializer()
        while len(ServerStream1_serializer) > 0:
            chunk, ServerStream1_serializer =  ServerStream1_serializer[:10], ServerStream1_serializer[10:]
            deserializer1.update(chunk)

            for packet in deserializer1.nextPackets():
                if packet == ServerStream1:
                    print (str(packet.Linktomusic))
                else:
                    print ("Packet lost in transmission!")


    else:
        print ("Incorrect Auth Token. Value should be anything above 0")
        return(basicUnitTest())

if __init__ = "__main__":   
    basicUnitTest()
