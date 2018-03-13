# Python for COMP30024 Part A

import os

class Board:
	'''This represents the board in the game world!'''

	# Board structure
	board = {}
	# Move Type
	moveType = ''


	def __init__(self, board):
		self.board, self.moveType = self.parseBoard(board)

	def parseBoard(self, boardStr):
		'''This parses the input into a dictionary for processing. 
		Also returns the type of move.'''
		newBoard = {}
		boardType = ''
		row = 0
		col = 0

		for coordinate in boardStr.split():
			if row == 8:
				boardType = coordinate
				break

			#print("Parsing: " + coordinate + " at " + str((col,row)))
			newBoard[(col,row)] = coordinate
			col += 1
			if col == 8:
				row += 1
				col = 0
				continue

		return newBoard, boardType


	def printBoard(self):
		'''Prints the board!'''
		for coords, values in self.board.items():
			print(values, end=' ')
			if coords[0] == 7:
				print('\n')
		return

	def printBoardType(self):
		'''Prints the type of move'''
		print(self.moveType)


# Testing 
boardStr = """
X - - - O O - X
- - - O - O O -
O - O - - - - @
- - - O O O - @
O O O - - @ @ -
- @ @ - @ @ @ -
- @ @ @ - - - -
X - - - - - - X
Moves
"""
board = Board(boardStr)
board.printBoard()
board.printBoardType()
# print("Completed!")

os.system("pause")