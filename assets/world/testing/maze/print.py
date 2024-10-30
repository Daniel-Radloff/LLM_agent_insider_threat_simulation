if __name__ == "__main__":
  rows = []
  with open("collision_maze.csv",'r') as file:
    for line in file:
      rows.append(line.replace('32125','#').replace('0',' ').strip().split(','))
  print("="*len(rows))
  for line in rows:
    print(''.join(line))
  print('|' + "="*len(rows) + '|')


