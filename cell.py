'''
Cell.py to handle cells
Cell class with attributes that are used with all cells to determine appropriate actions
Input: Executive calls class to make changes to specfic cell
Output: Sends cell object back to Executive for functionality

No External Sources

Authors: Abdulaziz Arab, Felix Balandran, Jamareon Davis, John Vitha, Riley Backus, William Grimsley
Creation Date: September 9, 2026
'''
class Cell:
    def __init__(self):
        self.has_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.adjacent_mines = 0
