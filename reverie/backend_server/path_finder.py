"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: path_finder.py
Description: Implements various path finding functions for generative agents.
Some of the functions are defunct. 
"""
import numpy as np

# Review Note:
# Removing unused code

# Review Note:
# this whole function needs to be refactored.
def path_finder_v2(maze, start, end, collision_block_char, verbose=False):
# Review Note:
# m: matrix?
# k: what we are looking for?
# maze: path_finder_v2 function parameter
  def make_step(blind_maze, step_number):
    for row in range(len(blind_maze)):
      for col in range(len(blind_maze[row])):
          # checks if a position is equal to something, and then does a thing?!?!??! 
          # it checks each direction it can move in and then moves in each one?
        if blind_maze[row][col] == step_number:
          if row>0 and blind_maze[row-1][col] == 0 and maze[row-1][col] == 0:
            blind_maze[row-1][col] = step_number + 1
          if col>0 and blind_maze[row][col-1] == 0 and maze[row][col-1] == 0:
            blind_maze[row][col-1] = step_number + 1
          if row<len(blind_maze)-1 and blind_maze[row+1][col] == 0 and maze[row+1][col] == 0:
            blind_maze[row+1][col] = step_number + 1
          if col<len(blind_maze[row])-1 and blind_maze[row][col+1] == 0 and maze[row][col+1] == 0:
             blind_maze[row][col+1] = step_number + 1

  # this can be reworked
  new_maze = []
  for row in maze: 
    new_row = []
    for block in row:
      if block == collision_block_char: 
        new_row.append(1)
      else: 
        new_row.append(0)
    new_maze.append(new_row)
  maze = new_maze

  # Review Note: Makes a 0 initialized matrix with same dimentions as passed in matrix
  blind_maze = []
  for array in maze:
      new_array = [0] * len(array)
      blind_maze.append(new_array)
  start_x,start_y = start
  end_x, end_y = end
  blind_maze[start_x][start_y] = 1 

  step = 0
  # Review Note: Removing except_handle becauseits never used
  while blind_maze[end_x][end_y] == 0:
      step += 1
      # Review Note: this seems very sus, because the step and the maze bounry can both be 1
      make_step(blind_maze, step)

  k = blind_maze[end_x][end_y]
  the_path = [(end_x,end_y)]
  # Re traces the steps in the path from the end. and builds co-ordinates like that.
  while k > 1:
    if end_x > 0 and blind_maze[end_x - 1][end_y] == k-1:
      end_x, end_y = end_x-1, end_y
      the_path.append((end_x, end_y))
      k-=1
    elif end_y > 0 and blind_maze[end_x][end_y - 1] == k-1:
      end_x, end_y = end_x, end_y-1
      the_path.append((end_x, end_y))
      k-=1
    elif end_x < len(blind_maze) - 1 and blind_maze[end_x + 1][end_y] == k-1:
      end_x, end_y = end_x+1, end_y
      the_path.append((end_x, end_y))
      k-=1
    elif end_y < len(blind_maze[end_x]) - 1 and blind_maze[end_x][end_y + 1] == k-1:
      end_x, end_y = end_x, end_y+1
      the_path.append((end_x, end_y))
      k -= 1
        
  the_path.reverse()
  return the_path


def path_finder(maze, start, end, collision_block_char, verbose=False):
    # Review Note: I have no idea why these are flipped, might need to go back and check 
    # my previous naming in the path finder function but it will be rewritten anyways so there is no point
  # EMERGENCY PATCH
  start = (start[1], start[0])
  end = (end[1], end[0])
  # END EMERGENCY PATCH

  path = path_finder_v2(maze, start, end, collision_block_char, verbose)

  new_path = []
  for i in path: 
    new_path += [(i[1], i[0])]
  path = new_path
  
  return path

if __name__ == '__main__':
  maze = [['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'], 
          [' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', '#'], 
          ['#', ' ', '#', ' ', ' ', '#', '#', ' ', ' ', ' ', '#', ' ', '#'], 
          ['#', ' ', '#', ' ', ' ', '#', '#', ' ', '#', ' ', '#', ' ', '#'], 
          ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', '#'], 
          ['#', '#', '#', ' ', '#', ' ', '#', '#', '#', ' ', '#', ' ', '#'], 
          ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' '], 
          ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#']]
  start = (0, 1)
  end = (0, 1)
  print (path_finder(maze, start, end, "#"))
