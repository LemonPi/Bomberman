from Enums import *

class Direction(object):
	def __init__(self, name, dx, dy, action, bomb_action):
		'''
		name: the name of the Direction 
		dx: the horizontal change to move in this Direction
		dy: the vertical change to move in this Direction
		action: the PlayerAction which moves in this direction
		bombaction: the PlayerAction which places a bomb and then move in this direction
		'''
		self.name=name
		self.dx=dx
		self.dy=dy
		self.action = action
		self.bombaction = bomb_action

	def __str__(self):
		return self.name

	def __eq__(self, other):
		return (self.dx == other.dx and self.dy == other.dy and self.action == other.action and self.bombaction == other.bombaction)

	def __ne__(self, other):
		return not self.__eq__(other)

	def __hash__(self):
		return hash("{0}{1}{2}{3}".format(self.dx, self.dy, self.action, self.bombaction))



UP = Direction('up', 0, -1, 'MOVEUP', 'BOMBANDMOVEUP')
DOWN = Direction('down', 0, 1, 'MOVEDOWN', 'BOMBANDMOVEDOWN')
RIGHT = Direction('right', 1, 0, 'MOVERIGHT', 'BOMBANDMOVERIGHT')
LEFT = Direction('left', -1, 0, 'MOVELEFT', 'BOMBANDMOVELEFT')
STILL = Direction('still', 0, 0, 'STAYPUT', 'PLACEBOMB')

# Keeps track of all available directions
Directions = {'up':UP, 'down':DOWN, 'left':LEFT, 'right': RIGHT, 'still':STILL}

# keeps track of the opposite directions
Opposite = {'up':DOWN, 'down':UP, 'left':RIGHT, 'right':LEFT, 'still':STILL}

'''
Keeps track of perpendicular directions.

Entry schema: 
direction:[direction to the right of it, direction to the left of it]
'''
Perpendicular = { 'up':[RIGHT, LEFT], 'down':[LEFT, RIGHT], 'left':[UP, DOWN], 'right':[DOWN, UP], 'still':[STILL, STILL]}
