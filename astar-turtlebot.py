import math
import sys
import numpy as np
import matplotlib.pyplot as plt
import pygame
from pygame.locals import QUIT, MOUSEBUTTONUP


#Turtlebot parameters
radius = 0.177
clearance = 0.2
L = 0.230#http://robotics.caltech.edu/wiki/images/9/9a/CSME133a_Lab2_Instructions.pdf
rpm1 = 10
rpm2 = 20
dtime = 2
r_wheel = 0.038

visited = []
allnodes = []
parent = []
current = []
cost_list = []
heuristic_cost = []
parent_visited = []
velocity=[]
velocity_new=[]
solution = []
vel_to_goal=[]

start_x = int(input("Enter x coordinate of start position: "))
start_y = int(input("Enter y coordinate of start position: "))
theta = int(input("Enter the robot orientation in radians: "))
goal_x = int(input("Enter x coordinate of goal position: "))
goal_y = int(input("Enter y coordinate of goal position: "))

def obstacle(x,y):
    obs = 0
    #center circle
    if ((x)**2 + (y)**2) <= (1+radius + clearance)**2:
#        print("c1")
        obs = 1
    #topright circle
    elif((x-2.00)**2 + (y-3.00)**2) <= (1+radius + clearance)**2:
#        print("c2")
        obs = 1
    #bottomright circle
    elif((x-2.00)**2 + (y+3.00)**2) <= (1+radius + clearance)**2:
#        print("c3")
        obs = 1
    #bottomleft circle
    elif((x+2.00)**2 + (y+3.00)**2) <= (1+radius + clearance)**2:
#        print("c4")
        obs = 1
    #right square
    elif(y-0.25-radius - clearance)<=0 and (y+0.25+radius + clearance)>=0 and (x-3.25+radius + clearance)>=0 and (x-4.75-radius - clearance)<=0:
#        print("s1")
        obs = 1
    #topleft square
    elif(y-3.75-radius - clearance)<=0 and (y-3.25+radius + clearance)>=0 and (x+1.25-radius - clearance)<=0 and (x+2.75+radius + clearance)>=0:
#        print("s2")
        obs = 1
    #left square
    elif(y-0.25-radius - clearance)<=0 and (y+0.25+radius + clearance)>=0 and (x+3.25-radius - clearance)<=0 and (x+4.75+radius + clearance)>=0:
#       print("s3")
       obs = 1
#    elif x>=(5-radius - clearance) or x<=(-5+radius + clearance) or y>=(5-radius - clearance) or y<=(-5+radius + clearance):
#        obs = 1
    elif x>=5 or y>=5 or x<=(-5) or y<=(-5):
#        print("o")
        obs = 1
    return obs  

def CheckStart(x,y):
    if obstacle(x,y) or x not in range(-5,5) or y not in range(-5,5):
        print("Start position invalid")
        return False
    else:
        return True

def CheckGoal(x,y):
    if obstacle(x,y) or x not in range(-5,5) or y not in range(-5,5):
        print("Goal position invalid")
        return False
    else:
        return True

if CheckStart(start_x,start_y) == False or CheckGoal(goal_x, goal_y) == False:
    print(sys.exit())
else:pass

start = [float(start_x),float(start_y)]
goal_pos = [float(goal_x),float(goal_y)]

allnodes.append(start)
parent.append(start)
current.append(start)
cost_list.append(99999)
heuristic_cost.append(99999)

cumulative_cost = 0

least_val = 0
velocity.append([0,0])
theta_list=[]
theta_list.append(theta)

goal_flag = 0

def check_near_visited(current, visited):
    for v in visited:
        if (((current[0] - v[0])**2 + (current[1] - v[1])**2) < (0.1)**2):
            return True
    return False

def heuristic(current, goal_pos):
    cost = math.sqrt((current[0] - goal_pos[0])**2 + (current[1] - goal_pos[1])**2) 
    cost = round(cost, 2)
    return cost

def IsMoveWorthy(current, initial,left_vel,right_vel,dt):
    h = heuristic(initial,current)
    cost_to_go = heuristic(current, goal_pos)
    cost_to_come = h +cumulative_cost 
    total_cost = cost_to_come + cost_to_go

    obs = obstacle(current[0],current[1])
    been_there_done_that = check_near_visited(current, visited)
    if current not in visited and obs == 0 and been_there_done_that == False :
        if current in allnodes:
            check = allnodes.index(current)    
            check_cost = heuristic_cost[check]
            if check_cost <= total_cost:
                pass
            else:
                allnodes.pop(check)
                allnodes.append(current)
                cost_list.pop(check)
                cost_list.append(cost_to_come)
                parent.pop(check)
                parent.append(initial)
                heuristic_cost.pop(check)
                heuristic_cost.append(total_cost)
                velocity.pop(check)
                velocity.append([left_vel, right_vel])
                theta_list.pop(check)
                theta_list.append(dt)                             
        else:
            allnodes.append(current)
            cost_list.append(cost_to_come)
            parent.append(initial)
            heuristic_cost.append(total_cost)
            velocity.append([left_vel, right_vel])
            theta_list.append(dt)  
    else:
        pass
        
def robot_move(left_vel, right_vel, initial,theta):
    x_robot = initial[0]
    y_robot = initial[1]
    for i in range(0,100):
        x_robot = x_robot + (r_wheel/2)*(left_vel + right_vel)*math.cos(theta)*dtime*(1/100)
        y_robot = y_robot + (r_wheel/2)*(left_vel + right_vel)*math.sin(theta)*dtime*(1/100)
        theta = theta + (r_wheel/L)*(right_vel-left_vel)*dtime*(1/100)
        obs = obstacle(x_robot,y_robot)
        if obs == 1:
            break            
    current = (x_robot, y_robot)
    return current, left_vel, right_vel, theta
  
def right_rpm1(vel1,vel2, initial,theta_list):
    current, ul, ur, dt = robot_move(vel1, vel2, initial,theta_list)
    IsMoveWorthy(current, initial,ul,ur,dt)
    
def left_rpm1(vel1,vel2, initial,theta_list):
    current, ul, ur, dt = robot_move(vel1, vel2, initial,theta_list)
    IsMoveWorthy(current, initial,ul,ur,dt)
    
def straight_rpm1(vel1,vel2, initial,theta_list):
    current, ul, ur, dt = robot_move(vel1, vel2, initial,theta_list)
    IsMoveWorthy(current, initial,ul,ur,dt)
    
def right_rpm2(vel1,vel2, initial,theta_list):
    current, ul, ur, dt = robot_move(vel1, vel2, initial,theta_list)
    IsMoveWorthy(current, initial,ul,ur,dt)
    
def left_rpm2(vel1,vel2, initial,theta_list):
    current, ul, ur, dt = robot_move(vel1, vel2, initial,theta_list)
    IsMoveWorthy(current, initial,ul,ur,dt)
    
def straight_rpm2(vel1,vel2, initial,theta_list):
    current, ul, ur, dt = robot_move(vel1, vel2, initial,theta_list)
    IsMoveWorthy(current, initial,ul,ur,dt)
    
def move_rpm12(vel1,vel2, initial,theta_list):
    current, ul, ur, dt = robot_move(vel1, vel2, initial,theta_list)
    IsMoveWorthy(current, initial,ul,ur,dt)
    
def move_rpm21(vel1,vel2, initial,theta_list):
    current, ul, ur, dt = robot_move(vel1, vel2, initial,theta_list)
    IsMoveWorthy(current, initial,ul,ur,dt)
        
def child(vel1, vel2, initial,theta_list):
    right_rpm1(0,vel1, initial,theta_list)
    left_rpm1(vel1,0, initial,theta_list)
    straight_rpm1(vel1,vel1, initial,theta_list)
    right_rpm2(0,vel2, initial,theta_list)
    left_rpm2(vel2,0, initial,theta_list)
    straight_rpm2(vel2,vel2, initial,theta_list)
    move_rpm12(vel1,vel2, initial,theta_list)
    move_rpm21(vel2,vel1, initial,theta_list)
        
def inside_goal_range(current):
    goal_flag=0
    if ((current[0]-goal_pos[0])**2+(current[1]-goal_pos[1])**2<(0.1)**2) or current == goal_pos:
        goal_flag=1
    return goal_flag

while goal_flag!=1:
    goal_flag = inside_goal_range(allnodes[least_val])   
    if allnodes==[]:
        print("Path not found for the given clearance")
        exit()
    child(rpm1, rpm2, allnodes[least_val],theta_list[least_val])
    visited.append(allnodes[least_val])
    parent_visited.append(parent[least_val])
    velocity_new.append(velocity[least_val])
    allnodes.pop(least_val)
    cost_list.pop(least_val)
    parent.pop(least_val)
    heuristic_cost.pop(least_val)
    velocity.pop(least_val)
    theta_list.pop(least_val)
#    print(len(visited))
    if heuristic_cost != []:
        min_cost = min(heuristic_cost)
        least_val  = heuristic_cost.index(min_cost)
        cumulative_cost = cost_list[least_val]
    


final_pos = visited[-1]
solution.append((round(final_pos[0],2), round(final_pos[1],2)))
vel_to_goal.append(velocity_new[-1])
#theta_final_list = []
#theta_final_list.append(theta_list[-1])

while True:
        check = visited.index(final_pos)
        final_pos = parent_visited[check] 
#        theta_temp = theta_list[check]
        solution.append((round(final_pos[0], 2), round(final_pos[1], 2)))
#        theta_final_list.append(theta_temp)
        vel_to_goal.append(velocity_new[check])
        if final_pos == start:
            print("Path Found")
            break
        
with open('velocity.txt', 'w') as filehandle:
    for v in vel_to_goal:
        filehandle.write("%s\n" % v)

def display_path(visited, path):
    x = np.linspace(-5,5,100)
    y = np.linspace(-5,5,100)
    print("visited: "+str(len(visited)))
    print("path: "+str(len(path)))       
 
    for i in visited:
        plt.scatter(i[0], i[1],s = 1, color = 'g')
    
    for i in path:
        plt.scatter(i[0], i[1], s = 1, color = 'b') 
    
    for i in x:
        for j in y:
            if obstacle(i,j) == True:
                plt.scatter(i, j, color = 'r')

    plt.scatter(goal_x, goal_y, s = 5, color = 'y')
    plt.scatter(start_x, start_y, s = 5, color = 'm')
    plt.axis('equal')  
    plt.show()
    
display_path(visited,solution)

def generate_obstacle_map():
    obstacle_list = []
    for x in range(-5,5):
        for y in range(-5,5):
            if obstacle(x,y):
                obstacle_list.append([x,y])
    return obstacle_list

obstacle_map = generate_obstacle_map()

"""
OBS_C = [219, 114, 15]
EXP_C = [36, 237, 130]
PATH_C = [230, 90, 104]
WHITE = [255, 255, 255]
START_C = [255, 0, 0]
GOAL_C = [0,0,255]
#preparing data for pygame
scale_factor = 100
obstacle_map = np.array(obstacle_map)
visited_nodes = np.array(visited)
solution = np.array(solution)
pygame.init()
size = (10*scale_factor, 10*scale_factor)
win = pygame.display.set_mode((10*scale_factor, 10*scale_factor))
win.fill(WHITE)
pygame.display.set_caption("A* algorithm turtlebot")
while True:
    win.fill(WHITE)
    pygame.event.get()
    for event in pygame.event.get():
        if event.type == MOUSEBUTTONUP:
            None
#    for obs in obstacle_map:
#        pygame.draw.rect(win, OBS_C, [(obs[0]+5)*scale_factor, (obs[1]+5)*scale_factor,10,10])
##        pygame.display.flip()
#        for event in pygame.event.get():
#            if event.type == MOUSEBUTTONUP:
#                None
        
    pygame.draw.rect(win, START_C, [(start_x+5)*scale_factor, (start_y+5)*scale_factor,3,3])
    pygame.draw.rect(win, GOAL_C, [(goal_x+5)*scale_factor, (goal_y+5)*scale_factor,3,3])
    pygame.draw.rect(win, OBS_C, [0.25*scale_factor, 5.25*scale_factor, 1.5*scale_factor, 0.5*scale_factor])
    pygame.draw.circle(win, OBS_C, [5*scale_factor, 5*scale_factor], 1*scale_factor)
    pygame.draw.circle(win, OBS_C, [7*scale_factor, 8*scale_factor], 1*scale_factor) #bottom right
    pygame.draw.circle(win, OBS_C, [7*scale_factor, 2*scale_factor], 1*scale_factor) #topright
    pygame.draw.circle(win, OBS_C, [3*scale_factor, 2*scale_factor], 1*scale_factor) #topleft
    pygame.display.flip()

    for vis in visited_nodes:
        pygame.draw.rect(win, EXP_C, [(vis[0]-5)*scale_factor, (vis[1]-5)*scale_factor,3,3])
        pygame.time.wait(1)
#        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                None
        
    for sol in solution:
        pygame.draw.rect(win, PATH_C, [(sol[0]+5)*scale_factor, (sol[1]+5)*scale_factor,3,3])
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
"""
