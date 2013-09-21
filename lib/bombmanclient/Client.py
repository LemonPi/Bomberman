from SocketChannel import SocketChannel, SocketChannelFactory
from BomberManProtocol_pb2 import *
import sys
import datetime
import traceback
import logging
import os

class BombmanClient():
  '''
  The client class for the bombman game
  '''
  channel=None
  PlayerMoves = {  
   'MOVEDOWN': MOVE_DOWN,
   'MOVEUP': MOVE_UP,
   'MOVELEFT': MOVE_LEFT,
   'MOVERIGHT': MOVE_RIGHT,
   'PLACEBOMB': PLACE_BOMB,
   'BOMBANDMOVELEFT': PLACE_BOMB_MOVE_LEFT,
   'BOMBANDMOVERIGHT': PLACE_BOMB_MOVE_RIGHT,
   'BOMBANDMOVEUP': PLACE_BOMB_MOVE_UP,
   'BOMBANDMOVEDOWN': PLACE_BOMB_MOVE_DOWN,
   'STAYPUT': STAY_STILL
      }

  def __init__(self):
    self.channelFactory = SocketChannelFactory()
  
  def validateMessage(self, protobufMsg):
    '''
    Check the protobuf message
    '''
    if not protobufMsg.IsInitialized():
      raise Exception("Message is missing required fields")

  # lists of lists which contains string of item on map
  def get_map_list(self, mapMessage, size):
    gamemap = [range(size.y) for x in range(size.x)]    
    for mapentry in mapMessage:
        gamemap[mapentry.pos.x][mapentry.pos.y] = mapentry.mapItem
    return gamemap
    
   # list of tuples of positions which has blocks
  def get_block_list(self, blocks):
    blocklist = []
    for block in blocks:
        blocklist.append((block.x, block.y))
    return blocklist
        
   # dictionary { playernumber : {'position', 'bomb_range', 'bomb_count'} }
  def get_player_position(self, players): 
    playersPos = {}
    for player in players:
        playersPos[player.playerNumber] = {'position':(player.pos.x, player.pos.y), 'bomb_range':player.bombRange, 'bomb_count':player.bombsLeft}
    return playersPos
  
  # dictionary { position : {'owner', 'ranage', 'time_left'} }
  def get_bomb_list(self, bombs):
    bomblist = {}
    for bomb in bombs:
      bomblist[(bomb.pos.x, bomb.pos.y)] = {'owner':bomb.owner, 'range':bomb.range, 'time_left':bomb.timeLeft}
    return bomblist

  # dictionary position : type
  def get_powerups(self, powerups):
    poweruplist = {}
    for powerup in powerups:
      poweruplist[(powerup.pos.x, powerup.pos.y)] = powerup.type
    return poweruplist
  
  # list of tuples of positions which has explosions
  def get_explosion_list(self, explosions):
    explosionlist = []
    for explosion in explosions: 
      explosionlist.append((explosion.x, explosion.y))
    return explosionlist

  def runClient(self, ai, host='localhost', port=19999, playername="BombmanPlayer"):
    '''
    The main loop in which the client receive message
    and send response containing the number generated
    by the AI.
    '''
    print "Starting client!!! My name is " + playername
    self.ai = ai
    if not os.path.exists(os.path.join(os.getcwd(), 'logs')):
      os.mkdir(os.path.join(os.getcwd(), 'logs'))
    logging.basicConfig(filename='logs/AI-{0}.log'.format(playername), level=logging.DEBUG)
    
    try:
      self.channel = self.channelFactory.openChannel(host, port)
    except Exception as e: 
      logging.exception("Unexcpected error when opening channel: ")
      return
    
    teamNameMessage = ClientWrapperMessage()
    
    teamNameMessage.messageType = NAME_RESPONSE
    teamNameMessage.name = playername; 
    
    self.channel.write(teamNameMessage.SerializeToString())

    while self.channel.connected:
      msg = BomberManMessage()
      msg.ParseFromString(self.channel.read())
      self.validateMessage(msg)

      if msg.messageType == START_GAME:
        maplist=self.get_map_list(msg.item, msg.mapSize)
        try:
          self.ai.new_game(self.get_map_list(msg.item, msg.mapSize), self.get_block_list(msg.blocks), self.get_player_position(msg.players), msg.playerNum)
        except:
          logging.exception("Unexpected error at new_game: ")
          break

        continue
      if msg.messageType == MOVE_REQUEST:
        starttime = datetime.datetime.now()
        try:
          move = ai.get_move(self.get_map_list(msg.item, msg.mapSize), self.get_bomb_list(msg.bombs), self.get_powerups(msg.powerups), self.get_player_position(msg.players), self.get_explosion_list(msg.explosions), msg.playerNum, msg.responseID)
        except:
          move = STAY_STILL
          logging.exception("Unexpected error during turn {0}:".format(msg.responseID))
          break

        wrapperMessage = ClientWrapperMessage()
        wrapperMessage.messageType = MOVE_RESPONSE
        wrapperMessage.moveResponse.PlayerID = msg.playerID
        wrapperMessage.moveResponse.playerNum = msg.playerNum
        wrapperMessage.moveResponse.responseID = msg.responseID
        if move in self.PlayerMoves: 
          wrapperMessage.moveResponse.response.move = self.PlayerMoves[move]
        else: 
          wrapperMessage.moveResponse.response.move = STAY_STILL

        self.channel.write(wrapperMessage.SerializeToString())
        diff = datetime.datetime.now() - starttime
        logging.info("message sent for move {0}: took {1} milliseconds".format(msg.responseID, diff.microseconds/1000))
        continue
      if msg.messageType == END_GAME:
        self.channel.close()
        continue

    self.channel.close()
    
    
    
    