#Player.py ai
import random

from bombmanclient.Client import *
from Enums import *
from Direction import *

import sys

sys.setrecursionlimit(10000)

# Walkable array with explosions trimmed out, because one does not simply walk into explosions
SAFE_WALKABLE = [Enums.MapItems.BLANK, Enums.MapItems.POWERUP]

enemy_lair_positions = [(1, 1), (15, 15)]


class PlayerAI():

	def __init__(self):
		self.blocks = []
		self.has_reached_enemy_lair = False

	def new_game(self, map_list, blocks_list, bombers, player_index):
		'''
		Called when a new game starts.
		
		map_list: a list of lists that describes the map at the start of the game

			e.g.
				map_list[1][2] would return the MapItem occupying position (1, 2)

		blocks_list: a list of tuples which indicates a block occupies the position indicated by the tuple

			e.g.
				if (2, 1) is in blocks_list then map_list[2][1] = MapItems.BLOCK

		bombers: a dictionary of dictionaries which contains the starting positions, bomb range and bombs available for both players. 
			use with player_index to find out information about the bomber. 
			
			key: an integer for player_index
			value: {'position': x, y coordinates of the bomber's position, 'bomb_range': bomb range, 'bomb_count': the number of bombs you have available }

			e.g.
				bombers[1]['bomb_range'] will give you the bomb range of a bomb if player 2 is to place a bomb in this turn. 

		player_index: yor player index.
			bombers[player_index][0] returns your starting position

		'''
		self.blocks = blocks_list[:]
		self.has_reached_enemy_lair = False

	def get_move(self, map_list, bombs, powerups, bombers, explosion_list, player_index, move_number):
		'''
		Wraps get_move_real to print out errors when an exception is raised.
		'''
		try:
			return self.get_move_real(map_list, bombs, powerups, bombers, explosion_list, player_index, move_number)
		except:
			traceback.print_exc()
			raise

	def get_move_real(self, map_list, bombs, powerups, bombers, explosion_list, player_index, move_number):
		'''
		Called when a move is requested by the game server

		Returns a string which represents the action that the Bomber should carry out in this turn. 
		Defaults to STAY_PUT if a string value that is not associated with a move/bomb move action is passed back. 

		Args: 
			map_list: a list of lists that describes the current map
				map_list[0][0] would return the MapItem occupying position (0, 0)
			
			bombs: a dictionary that contains information of bombs currently on the map. 
				key: a tuple of the bomb's location
				value: a dictionary with keys 'owner', 'range', 'time_left'

				e.g.
					bombs[(13, 5)]['owner'] will return the index of the Bomber who owns the bomb at (13, 5)

				No bombs with time_left = 0 will appear in this list.

			powerups: a dictionary that contains the power-ups currently on the map. 
				key: a tuple of the power-up's location
				value: a string which represents the type of power-up ('FIREUP' or 'BOMBUP').

				e.g.
					if powerups[(2, 3)] == 'FIREUP' then there is a FIREUP in position (2, 3)
			
			bombers: a dictionary that contains the player's current stats. 
				key: player index (0 or 1)
				value: a dictionay with keys 'position', 'bomb_range' and 'bomb_count'

				e.g.
					bombers[0]['bomb_range'] will return player 1's current bomb range. 

			explosion_list: a list of tuples that denotes the position of tiles which are currently exploding.

				By the next get_move call, all currently exploding tiles not be exploding. 
				However, in the next turn, another bomb may cause some of the same tiles to explode. 
			
			player_index: an integer representing your player index.
				bombers[player_index] returns the dictionary containing stats about your bomber
			
			move_number: the current turn number. Use to deterimine if you have missed turns. 
		'''

		bombMove = False
		my_position = bombers[player_index]['position']

		# updating the list of blocks
		for explosion in explosion_list:
			if explosion in self.blocks: 
				self.blocks.remove(explosion)

		validmoves = []
		neighbour_blocks = [] 

		# find out which directions Bomber can move to.
		for move in Directions.values():
			x = my_position[0] + move.dx
			y = my_position[1] + move.dy

			# Checks to see if neighbours are walkable, and stores the neighbours which are blocks
			if map_list[x][y] in SAFE_WALKABLE:
				# walkable is a list in enums.py which indicates what type of tiles are walkable
				validmoves.append(move)
			elif (x, y) in self.blocks: 
				neighbour_blocks.append((x, y))

		# there's no where to move to
		if len(validmoves) == 0: 
			return Directions['still'].action

		# can move somewhere, so choose a tile randomly
		move = validmoves[random.randrange(0, len(validmoves))]
		awayfrombombmoves = []

		# avoid bombs by maximizing our distance to bomb
		currentBestDist = 0
		for m in validmoves:
			x = my_position[0] + m.dx
			y = my_position[1] + m.dy
			disttobomb = distToNearestBomb(x, y, bombs, map_list)
			# print(disttobomb)
			if disttobomb > currentBestDist:
				awayfrombombmoves = [m]
				currentBestDist = disttobomb
			elif disttobomb == currentBestDist:
				awayfrombombmoves.append(m)

		awayfromenemymoves = []
		currentBestDist = 0

		enemy_index = 0 if player_index == 1 else 1
		enemy_position = bombers[enemy_index]['position']
		enemy_lair_position = enemy_lair_positions[enemy_index]

		path_to_other_lair_exists = path_exists(enemy_lair_position, my_position, map_list)
		finalmoves = awayfrombombmoves
		if not self.has_reached_enemy_lair and my_position == enemy_lair_position:
			self.has_reached_enemy_lair = True
		if path_to_other_lair_exists and len(self.blocks) > 5 and (not self.has_reached_enemy_lair):
			path_to_other_lair = find_path(my_position, enemy_lair_position, map_list)
			for m in awayfrombombmoves:
				x = my_position[0] + m.dx
				y = my_position[1] + m.dy
				if (x, y) == path_to_other_lair[-1]:
					finalmoves = [m]


		else:	# try to get away from the enemy - so maximize distance
			for m in awayfrombombmoves:
				x = my_position[0] + m.dx
				y = my_position[1] + m.dy
				disttoenemy = manhattan_distance((x, y), enemy_position)
				if disttoenemy > currentBestDist:
					awayfromenemymoves = [m]
					currentBestDist = disttoenemy
				elif disttoenemy == currentBestDist:
					awayfromenemymoves.append(m)

			finalmoves = awayfromenemymoves

		if len(finalmoves) > 0:
			move = finalmoves[random.randrange(0, len(finalmoves))]

		#if len(awayfrombombmoves) > 0:
		#	move = awayfrombombmoves[random.randrange(0, len(awayfrombombmoves))]

		if bombMove: 
			return move.bombaction
		else: 
			return move.action

def path_exists(start, end, map_list):
	''' 
	Takes two tuples that represents the starting, ending point and the currenet map to determine if a path between the two points exists on the map. 

	returns True if there is a path with no blocks, bombs or walls in it's path between start and end. 
	returns False otherwise. 

	Args: 
		start: a tuple which correspond to the starting point of the paths
		end: a tuple which correspond to the ending point of the path.
	'''
	open_list = [start]
	visited = []

	while len(open_list) != 0:
		current = open_list.pop(0)

		for direction in Directions.values():
			x = current[0] + direction.dx
			y = current[1] + direction.dy

			if (x, y) == end: 
				return True

			if (x, y) in visited: 
				continue

			if map_list[x][y] in SAFE_WALKABLE: 
				open_list.append((x, y))

			visited.append((x, y))

	return False

def manhattan_distance(start, end):
	'''
	Returns the Manhattan distance between two points. 

	Args:
		start: a tuple that represents the coordinates of the start position. 
		end: a tuple that represents the coordinates of the end postion
	'''
	return (abs(start[0]-end[0])+abs(start[1]-end[1]))

def find_path(start, end, map_list):
	''' Finds the closest path from point a to point b.
	based on http://theory.stanford.edu/~amitp/game-programming/a-star-flash/Pathfinder.as
	'''
	# g = already travelled, h = approx. how much to travel still, 
	initialobj = {'node': start, 'open': True, 'closed': False, 'parent': None, 'g': 0, 'h': manhattan_distance(start, end), 'f': manhattan_distance(start, end)}
	bopen = [initialobj]
	bvisited = {initialobj['node']: initialobj}
	while len(bopen) > 0:
		bopen.sort(key=lambda a: a['f']) # sort the array to find the one with the lowest approximate distance to the goal
		best = bopen.pop(0)
		best['open'] = False
		if best['node'] == end: # finished
			# todo retrace the path
			
			return retrace_path(bvisited, best, start)
		for direction in Directions.values():
			if direction == STILL:
				continue
			x = best['node'][0] + direction.dx
			y = best['node'][1] + direction.dy
			if not map_list[x][y] in SAFE_WALKABLE:
				continue
			newnode = (x, y)
			dist = manhattan_distance(best['node'], newnode)
			nodeobj = None
			try:
				nodeobj = bvisited[newnode]
			except KeyError:
				nodeobj = {'node': newnode, 'open': False, 'closed': False, 'parent': best, 'g': 999999, 'h': 999999, 'f': 999999}
				bvisited[newnode] = nodeobj
			# calculate the new g value - already travelled
			new_g = best['g'] + dist
			if new_g < nodeobj['g']: # first time seeing it or new cost is better than old cost (taking different path)
						# if true, use this path to travel to it
				if not nodeobj['open']:
					nodeobj['open'] = True
					bopen.append(nodeobj)
				nodeobj['g'] = new_g # update to the shorter value
				nodeobj['h'] = manhattan_distance(newnode, end)
				nodeobj['f'] = new_g + nodeobj['h']
				nodeobj['parent'] = best
	return None

def retrace_path(bvisited, best, start):
	path = []
	curvisited = best
	while curvisited != None and curvisited['node'] != start:
		path.append(curvisited['node'])
		curvisited = curvisited['parent']
	return path


def findAllPossibleExplosionPoints(bombs, block):
	locs = []
	explosioncanspread = [Enums.MapItems.BLANK, Enums.MapItems.POWERUP, Enums.MapItems.BOMB]
	for blocation in bombs:
		b = bombs[blocation]
		bx = blocation[0]
		by = blocation[1]
		brange = b['range']
		for xr in range(-brange, brange + 1):
			blockatloc = block[bx + xr][by]
			if blockatloc in explosioncanspread:
				locs.append((bx+xr, by))
		for yr in range(-brange, brange + 1):
			blockatloc = block[bx][by + yr]
			if blockatloc in explosioncanspread:
				locs.append((bx, by+yr))
	return locs

def findPossibleExplosionPoints(blocation, bombs, block):
	locs = []
	explosioncanspread = [Enums.MapItems.BLANK, Enums.MapItems.POWERUP, Enums.MapItems.BOMB]
	b = bombs[blocation]
	bx = blocation[0]
	by = blocation[1]
	brange = b['range']
	for xr in range(-brange, brange + 1):
		try:
			blockatloc = block[bx + xr][by]
			if blockatloc in explosioncanspread:
				locs.append((bx+xr, by))
		except IndexError:
			pass
	for yr in range(-brange, brange + 1):
		try:
			blockatloc = block[bx][by + yr]
			if blockatloc in explosioncanspread:
				locs.append((bx, by+yr))
		except IndexError:
			pass
	return locs

def distToNearestBomb(x, y, bombs, block):
	mindist = 99999
	minbomb = None
	for blocation in bombs:
		b = bombs[blocation]
		bx = blocation[0]
		by = blocation[1]
		brange = b['range']
		explosionlocs = findPossibleExplosionPoints(blocation, bombs, block)
		if not (x, y) in explosionlocs:
			continue
		# can explode on us
		distToUs = abs(x - bx) if y == by else abs(y - by)
		if distToUs < mindist:
			minbomb = blocation
			mindist = distToUs
	return mindist

def countBombs(bombs):
	players = {}
	for blocation in bombs:
		b = bombs[blocation]
		bowner = b['owner']
		try:
			players[bowner] += 1
		except KeyError:
			players[bowner] = 1
	return players
		
