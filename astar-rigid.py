import math
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import sys
import pygame
from pygame.locals import QUIT, MOUSEBUTTONUP
import numpy as np
import time

xmax = 300
ymax = 200

start_x = int(input("Enter x coordinate of start position: "))
start_y = int(input("Enter y coordinate of start position: "))
goal_x = int(input("Enter x coordinate of goal position: "))
goal_y = int(input("Enter y coordinate of goal position: "))

radius = int(input("Enter radius of the robot: "))
clearance = int(input("Enter clearance of the robot: "))

def obstacle(x,y):
    flag = 0
    flag_1 = 0
    flag_2 = 0
    point = Point(x,y)
    rectangle = Polygon([(35, 76), (100, 39),(95, 30), (30, 68)])
    complex_polygon = Polygon([(25, 185), (75, 185),(100, 150), (75, 120), (50,150), (20,120)])
    kite = Polygon([(225, 40), (250, 25),(225, 10), (200, 25)])
    #kite
    kite_line_1 = ((y-25)*25) + ((x-200)*15)
    kite_line_2 = ((y-10)*25) - ((x-225)*15)
    kite_line_3 = ((y-25)*25) + ((x-250)*15)
    kite_line_4 = ((y-40)*25) - ((x-225)*15)
    
    #rectangle
    rect_line_1 = ((y-76)*65) + ((x-35)*37)
    rect_line_2 = ((y-39)*5) - ((x-100)*9)
    rect_line_3 = ((y-30)*65) + ((x-95)*38)
    rect_line_4 = ((y-68)*5) - ((x-30)*8)
    
    #complex polygon
    quad_1_1 = 5*y+6*x-1050
    quad_1_2 = 5*y-6*x-150
    quad_1_3 = 5*y+7*x-1450
    quad_1_4 = 5*y-7*x-400
    
    quad_2_1 = ((y-185)*5) - ((x-25)*65)
    quad_2_2 = ((y-120)*30) - ((x-20)*30)
    quad_2_3 = ((y-150)*25) - ((x-50)*35)
    quad_2_4 = ((y-185)*(-50))
    
    #check kite
    if kite_line_1 > 0 and kite_line_2 > 0 and kite_line_3 < 0 and kite_line_4 < 0 or point.distance(kite) <= radius+clearance:
        flag = 1
    
    #check rectangle
    if rect_line_1 < 0 and rect_line_2 > 0 and rect_line_3 > 0 and rect_line_4 < 0 or point.distance(rectangle) <= radius+clearance:
        flag = 1
    
    #check polygon
    if quad_1_1>0 and quad_1_2>0 and quad_1_3<0 and quad_1_4<0:
        flag_1 = 1
    else:
        flag_1 = 0

    if quad_2_1 < 0 and quad_2_2 > 0 and quad_2_3 > 0 and quad_2_4 > 0:
        flag_2 = 1
    else:
        flag_2 = 0

    if flag_1 == 1 or flag_2 == 1 or point.distance(complex_polygon) <= radius+clearance:
        flag = 1
    
    #circle
    if(((x - (225))**2 + (y - (150))**2 - (25+radius+clearance)**2) <= 0) :
        flag = 1
        
    #ellipse
    if (((x - (150))/(40+radius+clearance))**2 + ((y - (100))/(20+radius+clearance))**2 - 1) <= 0:
        flag = 1    
    return flag

#Function used to draw the obstacle space for animation 
def draw_obstacle(x,y):
    flag = 0    
    point = Point(x,y)
    rectangle = Polygon([(35, 76), (100, 39),(95, 30), (30, 68)])
    complex_polygon = Polygon([(25, 185), (75, 185),(100, 150), (75, 120), (50,150), (20,120)])
    kite = Polygon([(225, 40), (250, 25),(225, 10), (200, 25)])
    #circle
    if(((x - (225))**2 + (y - (150))**2 - (25)**2) <= 0) :
        flag = 1
    #ellipse
    if (((x - (150))/(40))**2 + ((y - (100))/(20))**2 - 1) <= 0:
        flag = 1
    #check if point is inside polygon
    if rectangle.contains(point) == True:
        flag = 1
    if complex_polygon.contains(point) == True:
        flag = 1
    if kite.contains(point) == True:
        flag = 1
    return flag

def generate_obstacle_map():
    obstacle_list = []
    for x in range(0,xmax+1):
        for y in range(0,ymax+1):
            if draw_obstacle(x,y):
                obstacle_list.append([x,y])
    return obstacle_list


def CheckStart(x,y):
    if obstacle(x,y) or x not in range(0,xmax+1) or y not in range(0,ymax+1):
        print("Start position invalid")
        return False
    else:
        return True


def CheckGoal(x,y):
    if obstacle(x,y) or x not in range(0,xmax+1) or y not in range(0,ymax+1):
        print("Goal position invalid")
        return False
    else:
        return True

if CheckStart(start_x,start_y) == False or CheckGoal(goal_x, goal_y) == False:
    print(sys.exit())
else:pass

start = [start_x, start_y]
goal = [goal_x, goal_y]

allnodes = []
parent = []
cost_list = []
visited_nodes = []
temp = []
solution = []
cost_final_list=[]

allnodes.append(start)
parent.append(start)
solution.append(goal)

cost_list.append(99999)
cost_final_list.append(99999)
new_parent=[]

new_index=0
cumulative_cost=0

animation_flag = 0
tic = time.time()

def heuristic(c,g):
    h=math.sqrt((c[0]-g[0])**2+(c[1]-g[1])**2) # euc
    return h

def euclidean_heuristics(x1,y1,x2,y2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

def MoveRight(prev_node):
    current=prev_node[:]
    x=current[0]+1
    y=current[1]
    cost_to_go = euclidean_heuristics(goal_x, goal_y, x, y)
    cost=1+cumulative_cost
    cost_total=cost+cost_to_go
    IsMoveWorthy(x,y,cost,cost_total,prev_node)


def MoveDown(prev_node):
    current=prev_node[:]
    x=current[0]
    y=current[1]-1
    cost_to_go = euclidean_heuristics(goal_x, goal_y, x, y)
    cost=1+cumulative_cost
    cost_total=cost+cost_to_go
    IsMoveWorthy(x,y,cost,cost_total,prev_node)

def MoveLeft(prev_node):
    current=prev_node[:]
    x=current[0]-1
    y=current[1]
    cost_to_go = euclidean_heuristics(goal_x, goal_y, x, y)
    cost=1+cumulative_cost
    cost_total=cost+cost_to_go
    IsMoveWorthy(x,y,cost,cost_total,prev_node)

def MoveUp(prev_node):
    current=prev_node[:]
    x=current[0]
    y=current[1]+1
    cost_to_go = euclidean_heuristics(goal_x, goal_y, x, y)
    cost=1+cumulative_cost
    cost_total=cost+cost_to_go
    IsMoveWorthy(x,y,cost,cost_total,prev_node)
    
def MoveUpRight(prev_node):
    current=prev_node[:]
    x=current[0]+1
    y=current[1]+1
    cost_to_go = euclidean_heuristics(goal_x, goal_y, x, y)
    cost=math.sqrt(2)+cumulative_cost
    cost_total=cost+cost_to_go
    IsMoveWorthy(x,y,cost,cost_total,prev_node)
    
def MoveDownRight(prev_node):
    current=prev_node[:]
    x=current[0]+1
    y=current[1]-1
    cost_to_go = euclidean_heuristics(goal_x, goal_y, x, y)
    cost=math.sqrt(2)+cumulative_cost
    cost_total=cost+cost_to_go
    IsMoveWorthy(x,y,cost,cost_total,prev_node)

def MoveDownLeft(prev_node):
    current=prev_node[:]
    x=current[0]-1
    y=current[1]-1
    cost_to_go = euclidean_heuristics(goal_x, goal_y, x, y)
    cost=math.sqrt(2)+cumulative_cost
    cost_total=cost+cost_to_go
    IsMoveWorthy(x,y,cost,cost_total,prev_node)

def MoveUpLeft(prev_node):
    current=prev_node[:]
    x=current[0]-1
    y=current[1]+1
    cost_to_go = euclidean_heuristics(goal_x, goal_y, x, y)
    cost=math.sqrt(2)+cumulative_cost
    cost_total=cost+cost_to_go
    IsMoveWorthy(x,y,cost,cost_total,prev_node)
    
def iteration(node):
    MoveUp(node)
    MoveRight(node)
    MoveDown(node)
    MoveLeft(node)
    MoveUpRight(node)
    MoveDownRight(node)
    MoveDownLeft(node)
    MoveUpLeft(node)


def IsMoveWorthy(x,y,cost,cost_total,initial):
    flag=obstacle(x,y)
    current = []
    current.append(x)
    current.append(y)
    if x in range(0,xmax+1) and y in range(0,ymax+1) and flag==0:
        if current not in visited_nodes:
            if current in allnodes:
                check=allnodes.index(current)
                prev_cost=cost_final_list[check]
                if prev_cost<=cost_total:
                    pass
                else:
                    allnodes.pop(check)
                    cost_list.pop(check)
                    cost_final_list.pop(check)
                    parent.pop(check)
                    allnodes.append(current)
                    cost_list.append(cost)
                    cost_final_list.append(cost_total)
                    parent.append(initial)
            else:
                allnodes.append(current)
                cost_list.append(cost)
                cost_final_list.append(cost_total)
                parent.append(initial)
        else:
            pass
    return current,cost

print("Solving...")

while goal not in visited_nodes:
    iteration(allnodes[new_index])
    visited_nodes.append(allnodes[new_index])
    new_parent.append(parent[new_index])
    allnodes.pop(new_index)
    cost_list.pop(new_index)
    cost_final_list.pop(new_index)
    parent.pop(new_index)
    
    if cost_final_list != []:
        in_costh=min(cost_final_list)
        index=cost_final_list.index(in_costh)
        cumulative_cost=cost_list[index]
        new_index=index
while goal != [start_x, start_y]:
    if goal in visited_nodes:
        goal_index=visited_nodes.index(goal)
        goal=new_parent[goal_index]
        solution.append(goal)
    
toc = time.time()    
print("Time to solve: "+str((toc-tic)/60))
print("Length of path to reach goal: "+str(len(solution)))
print("Number of nodes explored: "+str(len(visited_nodes)))

obstacle_map = generate_obstacle_map()
            
OBS_C = [219, 114, 15]
EXP_C = [36, 237, 130]
PATH_C = [230, 90, 104]
WHITE = [255, 255, 255]
START_C = [255, 0, 0]
GOAL_C = [0,0,255]
#preparing data for pygame
scale_factor = 3
obstacle_map = np.array(obstacle_map)
visited_nodes = np.array(visited_nodes)
solution = np.array(solution)
pygame.init()
size = (xmax*scale_factor, ymax*scale_factor)
win = pygame.display.set_mode((xmax*scale_factor, ymax*scale_factor))
win.fill(WHITE)
pygame.display.set_caption("A* algorithm rigid robot")
while True:
    win.fill(WHITE)
    pygame.event.get()
    for event in pygame.event.get():
        if event.type == MOUSEBUTTONUP:
            None
    for obs in obstacle_map:
        pygame.draw.rect(win, OBS_C, [obs[0]*scale_factor, (ymax-obs[1])*scale_factor,3,3])
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                None
        
    pygame.draw.rect(win, START_C, [start_x*scale_factor, (ymax-start_y)*scale_factor,3,3])
    pygame.draw.rect(win, GOAL_C, [goal_x*scale_factor, (ymax-goal_y)*scale_factor,3,3])
    pygame.display.flip()

    for vis in visited_nodes:
        pygame.draw.rect(win, EXP_C, [vis[0]*scale_factor, (ymax-vis[1])*scale_factor,3,3])
        pygame.time.wait(1)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                None
        
    for sol in solution:
        pygame.draw.rect(win, PATH_C, [sol[0]*scale_factor, (ymax-sol[1])*scale_factor,3,3])
        pygame.time.wait(1)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                None        
    animation_flag = 1
    while animation_flag == 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
