import sys, os
sys.path.append(os.path.join(os.getcwd(), "lib"))

from bombmanclient.Client import BombmanClient
from bombmanplayer.PlayerAI import PlayerAI

if __name__ == '__main__':
  
  if len(sys.argv) != 4:
    print "Usage: python runclient.py <host> <port> <playername>"
  else:
    host = sys.argv[1]
    port = int(sys.argv[2])
    playername = sys.argv[3]
    BombmanClient().runClient(PlayerAI(), host, port, playername)