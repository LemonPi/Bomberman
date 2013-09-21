#Player.py ai
import random

from bombmanclient.Client import *
from Enums import *
from Direction import *

class PlayerAI():

	def __init__(self):
		self.blocks = []

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

	def get_move(self, map_list, bombs, powerups, bombers, explosion_list, player_index, move_number):
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
			if map_list[x][y] in WALKABLE:
				# walkable is a list in enums.py which indicates what type of tiles are walkable
				validmoves.append(move)
			elif (x, y) in self.blocks: 
				neighbour_blocks.append((x, y))

		# place a bomb if there are blocks that can be destroyed
		if len(neighbour_blocks) > 0:
			bombMove = True

		# there's no where to move to
		if len(validmoves) == 0: 
			return Directions['still'].action

		# can move somewhere, so choose a tile randomly
		move = validmoves[random.randrange(0, len(validmoves))]

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

				if map_list[x][y] in walkable: 
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
		
