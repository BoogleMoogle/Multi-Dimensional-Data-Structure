# from copyreg import add_extension
# from textwrap import indent
# from typing import Self

from types import NoneType

from matplotlib.figure import figaspect
from matplotlib.lines import lineStyles
import matplotlib.pyplot as plt
import random
# from narwhals import col
from narwhals import col
from networkx import dag_longest_path
import pandas as pd
import os
from math import ceil
import matplotlib.style as mplstyle
import numpy as np

#to see stack
import inspect

#to turn off future warnings
import warnings

# from pygame import SCRAP_CLIPBOARD
warnings.simplefilter(action='ignore',category=FutureWarning)





class DAGTree:
    def __init__(self, points=[], depth=0, axis=0, split_value=None, bbox=[], left=None, right=None, middle=None, middle_child=False, parent=[], cuttoff=None):
        self.left = left
        self.right = right
        self.middle = middle
        self.parent = parent
        self.data_size = len(points)
        self.middle_child = middle_child

        if cuttoff == None:
            cuttoff = 4
        self.cuttoff = cuttoff

        if axis == 0:   #sort by x values
            points.sort()
        else:           #sort by y values
            points.sort(key=lambda x: x[1])     #!!!If range is too short then it will crash due to number of repeating values and recursion
        self.points=points

        self.depth=depth
        self.axis=axis
        self.split_value=split_value

        if len(bbox) == 0:      #only need to find bbox for first time
            self.bbox = self.find_bbox(bbox)
        else:
            self.bbox = bbox

        if self.parent == []:
            self.root = True
            # self.split_value = self.points[len(self.points)//2][0]
            self.split()


    #To String Method    
    def __str__(self):
        if self.split_value != None:
            if self.axis == 0:
                return f"Split Node: x = {self.split_value[self.axis]}, Level: {self.depth}"#, Left: {self.left}, Right: {self.right}"
            else:
                return f"Split Node: y = {self.split_value[self.axis]}, Level: {self.depth}"#, Left: {self.left}, Right: {self.right}"
        else:
            return f"{self.points}"


    #Bbox Method
    def find_bbox(self,bbox):
        for item in self.points:
                if len(bbox) == 0:
                    bbox=[item[0], item[1], item[0], item[1]]
                    #this sets the x min and max as the first x value and the same for the y min and max
                if bbox[0] > item[0]:       #xmin
                    bbox[0] = item[0]
                if bbox[1] > item[1]:       #ymin
                    bbox[1] = item[1]
                if bbox[2] < item[0]:       #xmax
                    bbox[2] = item[0]       
                if bbox[3] < item[1]:       #ymax
                    bbox[3] = item[1]
        return bbox


    #Split Method
    def split(self):
        if self.points != None:
            # print("Split!!!")
            # print(len(inspect.stack()))
            # with open(r"temp.txt", 'a') as file:
            #     file.write(f"{len(inspect.stack())}\n")
            #     file.close()

            #Points need to be sorted before being put in the left or right or middle child
            if self.axis == 0:
                self.points.sort()
            else:
                self.points.sort(key=lambda x: x[1])
            
            self.split_value = self.points[len(self.points)//2]

            # print(self.points)

            # self.connect()
            #Hard Splitting Method
            # right = self.points[(len(self.points)//2):]
            # left=self.points[:(len(self.points)//2)]
            
            #Soft Splitting Method          (ideal, but need more error checking)
            right, left = [], []
            for item in self.points:
                if item[self.axis] >= self.split_value[self.axis]:          #items with bigger value (right/up)
                    if item[self.axis] == self.split_value[self.axis]:              #need to check y values still
                        if item[(self.axis + 1) % 2] >= self.split_value[(self.axis + 1) % 2]:
                            right.append(item)
                        else:
                            left.append(item)
                    else:
                        right.append(item)
                else:                                                   #items with lesser value (left/down)
                    left.append(item)

            #for middle child
            middle = []
            # for i in range(ceil(len(left)/2)):   #rounded up left median posistion
                # middle.append(left[((len(left)//2))+i])       #hard splitting >:(
            
            # for i in range(ceil(len(right)//2)):
            #     middle.append(right[i])                       #hard splitting >:(

            for item in left:
                if item[self.axis] >= left[len(left)//2][self.axis]:                #checks on primary value
                    if item[self.axis] == left[len(left)//2][self.axis]:            #need to check secondary values still
                        if item[(self.axis + 1) % 2] >= left[len(left)//2][(self.axis + 1) % 2]:
                            middle.append(item)
                    else:
                        middle.append(item)
            
        
            for item in right:
                if item[self.axis] <= right[(len(right)//2)-1][self.axis]:
                    if item[self.axis] == right[(len(right)//2)-1][self.axis]:              #need to check secondary values still
                        if item[(self.axis + 1) % 2] <= right[(len(right)//2)-1][(self.axis + 1) % 2]:
                            middle.append(item)
                    else:
                        middle.append(item)

            # print(left)
            # print(right)
            # print(middle)
            # print("_"*50)
        
            if self.parent != [] and self.parent[0].data_size == self.data_size:
                # print(f"{self.parent[0].data_size}\t{self.data_size}")
                    return
            self.points = None
            if self.axis == 0:  #this is on the x axis
                # print(f"left, {self.axis}, {self.depth}")
                self.left = DAGTree(left, depth=self.depth+1, axis=1, bbox=[self.bbox[0], self.bbox[1], self.split_value[self.axis], self.bbox[3]], parent=[self], cuttoff=self.cuttoff, middle_child=self.middle_child)
                # print(f"right, {self.axis}, {self.depth}")
                self.right = DAGTree(right, depth=self.depth+1, axis=1, bbox=[self.split_value[self.axis], self.bbox[1], self.bbox[2], self.bbox[3]], parent=[self], cuttoff=self.cuttoff, middle_child=self.middle_child)
                if middle != []:
                    # print(f"middle, {self.axis}, {self.depth}")
                    self.middle = DAGTree(middle, depth=self.depth+1, axis=1, bbox=[middle[0][0],self.bbox[1],middle[len(middle)-1][0],self.bbox[3]], parent=[self], middle_child=True, cuttoff=self.cuttoff)
            else:               #this is on the y axis
                # print(f"left, {self.axis}, {self.depth}")
                self.left = DAGTree(left,  depth=self.depth+1, axis=0, bbox=[self.bbox[0], self.bbox[1], self.bbox[2], self.split_value[self.axis]], parent=[self], cuttoff=self.cuttoff, middle_child=self.middle_child)
                # print(f"right, {self.axis}, {self.depth}")
                self.right = DAGTree(right, depth=self.depth+1, axis=0, bbox=[self.bbox[0], self.split_value[self.axis], self.bbox[2], self.bbox[3]], parent=[self], cuttoff=self.cuttoff, middle_child=self.middle_child)
                if middle != []:
                    # print(f"middle, {self.axis}, {self.depth}")
                    self.middle = DAGTree(middle, depth=self.depth+1, axis=0, bbox=[self.bbox[0],middle[0][1],self.bbox[2],middle[len(middle)-1][1]], parent=[self], middle_child=True, cuttoff=self.cuttoff)
            
            if self.middle_child == True:
                self.left.connect()
                self.right.connect()
                if self.middle != None:
                    self.middle.connect()
            #the recursive call
            if self.left.data_size > self.cuttoff:
                self.left.split()
            if self.right.data_size > self.cuttoff:
                self.right.split()
            if self.middle.data_size > self.cuttoff:
                self.middle.split()


    #Single Range Cover Search Method
    def SRC(self, q_xmin, q_ymin, q_xmax, q_ymax):
        if q_xmin > q_xmax:
            temp = q_xmax
            q_xmax = q_xmin
            q_xmin = temp
        if q_ymin > q_ymax:
            temp = q_ymax
            q_ymax = q_ymin
            q_ymin = temp

        # if self.split_value == None:
        #     return self
        if self.bbox[0] <= q_xmin and self.bbox[2] >= q_xmax and self.bbox[1] <= q_ymin and self.bbox[3] >= q_ymax: #this node 100% contains the range
            # if self.axis == 1:
            if self.left != None:
                if self.left.bbox[2] >= q_xmax and self.left.bbox[3] > q_ymax:      #self.bbox[q_xmin,q_ymin,q_xmax,q_ymax]
                    return self.left.SRC(q_xmin, q_ymin, q_xmax, q_ymax)
            if self.right != None:
                if self.right.bbox[0] <= q_xmin and self.right.bbox[1] <= q_ymin:
                    return self.right.SRC(q_xmin, q_ymin, q_xmax, q_ymax)
            if self.middle != None:
                if self.middle.bbox[0] <= q_xmin and self.middle.bbox[2] >= q_xmax and self.middle.bbox[1] <= q_ymin and self.middle.bbox[3] >= q_ymax:     #we want to go down the middle first because it has the widest search
                    return self.middle.SRC(q_xmin, q_ymin, q_xmax, q_ymax)
            # else:
            #     return None
                
        else:
            if self.middle != None:
                if self.middle.bbox[0] <= q_xmin and self.middle.bbox[2] >= q_xmax and self.middle.bbox[1] <= q_ymin and self.middle.bbox[3] >= q_ymax:
                    return self.middle.SRC(q_xmin, q_ymin, q_xmax, q_ymax)
            elif self.left != None:
                if self.left.bbox[2] > q_xmax and self.left.bbox[3] >= q_ymax:
                    return self.left.SRC(q_xmin, q_ymin, q_xmax, q_ymax)
            elif self.right != None:
                if self.right.bbox[0] <= q_xmin and self.right.bbox[1] <= q_ymin:
                    return self.right.SRC(q_xmin, q_ymin, q_xmax, q_ymax)
        return self


    #BRC Linearly
    def linear_BRC(self,q_xmin,q_ymin,q_xmax,q_ymax):
        nodes = self.get_leaf_linear(boxes=[])
        
        temp = []
        for item in nodes:
            for thing in item:
                temp.append(thing)

        returning_list = []
        for item in temp:
            if item[0] >= q_xmin and item[0] <= q_xmax and item[1] >= q_ymin and item[1] <= q_ymax:
                returning_list.append(item)
        return returning_list


    #Return most top nodes as well
    def BRC(self, q_xmin, q_ymin, q_xmax, q_ymax, result=[]):
        if self.bbox[0] >= q_xmin and self.bbox[1] >= q_ymin and self.bbox[2] <= q_xmax and self.bbox[3] <= q_ymax: #FULLY in range of query
            if self.left != None:
                self.left.BRC(q_xmin, q_ymin, q_xmax, q_ymax, result)
            if self.right != None:
                self.right.BRC(q_xmin, q_ymin, q_xmax, q_ymax, result)
        # if self.middle != None:           #if we include middle then we are including repeating numbers that are not real
        #     self.middle.BRC(q_xmin, q_ymin, q_xmax, q_ymax, result)
        else:
            if self.bbox[0] <= q_xmin or self.bbox[1] <= q_ymin or self.bbox[2] >= q_xmax or self.bbox[3] >= q_ymax:
                if self.points != None:
                    for item in self.points:
                        if item[0] <= q_xmax and item[0] >= q_xmin and item[1] <= q_ymax and item[1] >= q_ymin:
                            result.append(item)
                else:
                    if self.left != None:                  
                        self.left.BRC(q_xmin, q_ymin, q_xmax, q_ymax, result)
                    if self.right != None:
                        self.right.BRC(q_xmin, q_ymin, q_xmax, q_ymax, result)
                    # if self.middle != None:
                    #     self.middle.BRC(q_xmin, q_ymin, q_xmax, q_ymax, result)
        return result
        



        # if self.bbox[0] >= q_xmin and self.bbox[1] >= q_ymin and self.bbox[2] <= q_xmax and self.bbox[3] <= q_ymax: #FULLY in range of query
        #     if self.left != None:
        #         self.left.BRC(q_xmin, q_ymin, q_xmax, q_ymax, result)
        #     if self.right != None:
        #         self.right.BRC(q_xmin, q_ymin, q_xmax, q_ymax, result)
        # else:
        #     if self.bbox[0] <= q_xmin or self.bbox[1] <= q_ymin or self.bbox[2] >= q_xmax or self.bbox[3] >= q_ymax:
        #         if self.points != None:
        #             for item in self.points:
        #                 if item[0] <= q_xmax and item[0] >= q_xmin and item[1] <= q_ymax and item[1] >= q_ymin:
        #                     result.append(item)
        #         else:
        #             if self.left != None:                  
        #                 self.left.BRC(q_xmin, q_ymin, q_xmax, q_ymax, result)
        #             if self.right != None:
        #                 self.right.BRC(q_xmin, q_ymin, q_xmax, q_ymax, result)
        # return result


    #Graph Tree Function
    def graph_tree(self,plot_boxes=None, middle=True):
        boxes = pd.DataFrame(self.itterate_through(),index=None,columns=['Axis','BBOX','Split Val','Depth','Points','Middle'])     #[self.axis,self.bbox,self.split_value[self.axis],self.depth,self.points,self.middle_child]
        middle_nodes = boxes.loc[boxes['Middle'] == True]
        leaf_points = pd.DataFrame(self.get_leaf_linear(),index=None,columns=['Axis','BBOX','Depth','Points'])['Points']           #[self.axis,self.bbox,self.depth,self.points]
        nodes = boxes.loc[boxes['Middle'] == False]
        
        print(f"Num of Nodes Made: {len(boxes)}")
        print("Graphing...")

        # leaf_points have the points, nodes have the normal bboxes, middle_nodes have the middle nodes
        points = leaf_points.dropna().values.tolist()
        x,y = [], []
        for item in points:
            x.append(item[0])
            y.append(item[1])
            
        plt.scatter(x, y, c='grey', marker='o')
 
        plt.vlines(x=self.bbox[2],ymin=self.bbox[1],ymax=self.bbox[3],color='black',linestyles=':')
        plt.vlines(x=self.bbox[0],ymin=self.bbox[1],ymax=self.bbox[3],color='black',linestyles=':')
        plt.hlines(y=self.bbox[3],xmin=self.bbox[0],xmax=self.bbox[2],color='black',linestyles=':')
        plt.hlines(y=self.bbox[1],xmin=self.bbox[0],xmax=self.bbox[2],color='black',linestyles=':')

        if type(middle) == str or middle == True:
            middle_bboxes = middle_nodes[['Axis','BBOX','Split Val']]
            middle_bboxes = middle_bboxes.dropna().values.tolist()
            for item in middle_bboxes:
                if item[0] == 1:   #x axis
                    plt.vlines(x=item[1][0],ymin=item[1][1],ymax=item[1][3],color='purple',linestyles='-.', alpha=0.2)
                    plt.vlines(x=item[1][2],ymin=item[1][1],ymax=item[1][3],color='purple',linestyles='-.', alpha=0.2)
                else:
                    plt.hlines(y=item[1][1],xmin=item[1][0],xmax=item[1][2],color='purple',linestyles='-.', alpha=0.2)
                    plt.hlines(y=item[1][3],xmin=item[1][0],xmax=item[1][2],color='purple',linestyles='-.', alpha=0.2)

        if type(middle) != str:
            nodes = nodes[['Axis','BBOX','Split Val']].dropna().values.tolist()
            for item in nodes:
                if item[0] == 0:
                    plt.vlines(x=item[2],ymin=item[1][1],ymax=item[1][3],color='blue',linestyles=':')
                else:
                    plt.hlines(y=item[2],xmin=item[1][0],xmax=item[1][2],color='red',linestyles=':')

        if plot_boxes != None:
            for item in plot_boxes:
                plt.hlines(y=item[1], xmin=item[0], xmax=item[2], color='green')
                plt.hlines(y=item[3], xmin=item[0], xmax=item[2], color='green')

                plt.vlines(x=item[0], ymin=item[1], ymax=item[3], color='green')
                plt.vlines(x=item[2], ymin=item[1], ymax=item[3], color='green')

        plt.tight_layout()
        return plt.show()


    #Get Leaf Method - Just returns a list of leaf nodes (being the points)
    def get_leaf_linear(self,boxes=[]):
        if self.points != None:
            boxes.append(self.points)
        if self.left != None:
            self.left.get_leaf_linear(boxes)
        if self.right != None:
            self.right.get_leaf_linear(boxes)
        return boxes


    #Itteratting Through Function
    def itterate_through(self,boxes=[],leaf=False,leaf_box=[]):
        '''
        Returns [self.axis, self.bbox, self.split_value[self.axis], and self.depth, self.points] in that order
        
        :param self: Description
        :param boxes: Description
        '''

        if self.split_value == None:
            boxes.append([self.axis,self.bbox,self.split_value,self.depth,self.points,self.middle_child])
        else:
            boxes.append([self.axis,self.bbox,self.split_value[self.axis],self.depth,self.points,self.middle_child])  #removed self.parent

        if self.left != None and self.left.parent[0] == self:
            self.left.itterate_through(boxes,leaf=leaf)
        if self.right != None and self.right.parent[0] == self:
            self.right.itterate_through(boxes,leaf=leaf)
        if self.middle != None and self.middle.parent[0] == self:
            self.middle.itterate_through(boxes,leaf=leaf)

        return boxes


    #Print Tree Function
    def print_tree(self,boxes=[],sort=False,whole=False,file=None):
        if self.left != None or self.right != None:
            boxes.append([self.axis,self.bbox,self.split_value[self.axis],self.depth,self.points,self.middle_child])
        
        if self.left != None:
            self.left.itterate_through(boxes)
            self.right.itterate_through(boxes)
            self.middle.itterate_through(boxes)

        if sort == True:
            boxes.sort(key=lambda x: x[3])
        if file == None:
            print("| Depth\t\t| Split\t\t| Middle\t\t| Range: [xmin, xmax] [ymin, ymax]\t\t| Points")
            for item in boxes:
                if item[0] == 1:
                    # print(f"| Depth: {item[3]}\t|  Y = {item[2]}\t| Middle: {item[5]}\t| BBOX: {item[1]}")
                    print(f"| Depth: {item[3]}\t|  Y = {item[2]}\t| Middle: {item[5]}\t\t| Range: [{item[1][0]}, {item[1][2]}] [{item[1][1]}, {item[1][3]}]\t\t| Points: {item[4]}")
                else:
                    print(f"| Depth: {item[3]}\t|  X = {item[2]}\t| Middle: {item[5]}\t\t| Range: [{item[1][0]}, {item[1][2]}] [{item[1][1]}, {item[1][3]}]\t\t| Points: {item[4]}")

            if whole == True:
                all_points = self.itterate_through(leaf=True)
                for item in all_points:
                    print(f"| Depth: {item[2]}\t| Range: [{item[1][0]}, {item[1][2]}] [{item[1][1]}, {item[1][3]}]\t\t| Points: {item[3]}")
        else:
            i=0
            temp = pd.DataFrame(columns=['Depth', 'Split', 'Middle','Range [xmin, xmax] [ymin, ymax]','Points'])
            for item in boxes:
                temp.loc[i] = item[3], item[2],item[5],f"[{item[1][0]}, {item[1][2]}] [{item[1][1]}, {item[1][3]}", item[4]
                i+=1
            temp.to_csv(file)


    #Connect Method - Checks if 2 nodes can be connected
    def connect(self, pTmp=None):
        if self.parent != [] and self.parent[0] != None and self != []:
            pTmp = self
            while pTmp.parent != []:            
                pTmp = pTmp.parent[0]
            pTmp = pTmp.middle
            points = self.points
            split_val = self.split_value
            important_node = pTmp.SRC(self.bbox[0], self.bbox[1], self.bbox[2], self.bbox[3])
            if important_node != None and important_node.bbox == self.bbox and important_node.data_size == self.data_size:
                # print(f"SRC Node: {important_node.bbox}\tSelf: {self.bbox}")
                if important_node.parent[0].left == important_node:
                    important_node.parent[0].left = self
                    self.parent.append(important_node.parent[0].left)
                elif important_node.parent[0].right == important_node:
                    important_node.parent[0].right = self
                    self.parent.append(important_node.parent[0].right)
                elif important_node.parent[0].middle == important_node:
                    # print(important_node.parent[0].middle)
                    important_node.parent[0].middle = self
                    # print(important_node.parent[0].middle)
                    self.parent.append(important_node.parent[0].middle)
                important_node = None
                self.points = points
                self.split_value = split_val
                # self.split()
                # print("Connect!")
                
                # print(f"Found Node: {important_node.parent[0]}\tOG Node: {self.parent[0]}")
                # with open("temp.txt",'a') as file:
                #     file.write("Connect\n")
                #     file.close()
                        


                

###### General Use Methods ######
def make_points(num=1, sprout=None, aRang=0, bRang=100, sort=False):

    temp = []
    if sprout != None:
        random.seed(sprout)
    while len(temp) < num:
        temp.append((random.randint(aRang,bRang),random.randint(aRang,bRang)))
    
    if sort == True:
        temp.sort()    
    return temp

    
def save_query(tree, xmin=None, ymin=None, xmax=None, ymax=None, query_list=None, num=1, sprout=None, path=None, small=False, medium=False, large=False, save=True, show=False, SRC=False, BRC=False):
    """
    This intakes a Tree, runs it through a searching method with randomly made bbox values, then saves a csv file to path. If path is not given it will create a .csv file in Saved Query, if no folder exists then it will create it. Currently works for SRC and BRC method, if neither SRC or BRC are stated as true when this method is called it will default to SRC.
    
    :param tree: The 3DAG Tree
    :param xmin: x minimum of search
    :param ymin: y minimum of search
    :param xmax: x maximum of search
    :param ymax: y maximum of search
    :param num: The amount of queries repeated
    :param sprout: Seed for random xmin, ymin, xmax, and y max
    :param path: Optional, need r before path string
    :param small: Generates random xmin and y min, then xmax and ymax are 6 points either above or below it (sorted later)
    :param medium: Generates random xmin and y min, then xmax and ymax are 20 points either above or below it (sorted later)
    :param large: Generates random xmin and y min, then xmax and ymax are 40 points either above or below it (sorted later)
    :param save: If False, will not save to file
    :param show: Calls graphing method for the boundry box either given or generated
    :param SRC: If True, will call SRC method for search
    :param BRC: If True, will call BRC method for search
    """
    if sprout != None:
        random.seed(sprout)
    if path == None:
        things = os.listdir('.')
        if things.__contains__('Saved Query') == False and things.__contains__('Saved Queries') == False:
            os.mkdir("Saved Query")
        path = f"Saved Query/temp {len(os.listdir('Saved Query'))+1}.csv"
    i=0     #counter

    if xmin==None and ymin==None and xmax==None and ymax==None and query_list==None:     #we need to generate query
        if small == True:
            coeff_num = int((tree.bbox[2]-tree.bbox[0])*0.1)
        if medium == True:
            coeff_num = int((tree.bbox[2]-tree.bbox[0])*0.2)
        if large == True:
            coeff_num = int((tree.bbox[2]-tree.bbox[0])*0.3)


        while i < num:      #could change with while num != 0
            xmin = random.randint(tree.bbox[0],tree.bbox[2]-coeff_num)
            xmax = random.randint(xmin+1,xmin+coeff_num)
            ymin = random.randint(tree.bbox[1],tree.bbox[3]-coeff_num)
            ymax = random.randint(ymin+1,ymin+coeff_num)

            #Arranges the queries xmins and ymins
            if xmin > xmax:
                a = xmax
                xmax = xmin
                xmin = a
            if ymin > ymax:
                a = ymax
                ymax = ymin
                ymin = a
            
            #This limits the possible query ranges to the actual boundery box of the data set
            if xmin < tree.bbox[0]:
                xmin = tree.bbox[0]

            if xmax > tree.bbox[2]:
                xmax = tree.bbox[2]

            if ymin < tree.bbox[1]:
                ymin = tree.bbox[1]

            if ymax > tree.bbox[3]:
                ymax = tree.bbox[3]
            
            if ymax < tree.bbox[1]:
                ymax = tree.bbox[1]
        
            #we need a default searching method
            if SRC == False and BRC == False:
                SRC = True

            if SRC == True:
                node = tree.SRC(q_xmin=xmin, q_ymin=ymin, q_xmax=xmax, q_ymax=ymax)
            elif BRC == True:
                # node = tree.BRC(q_xmin=xmin, q_ymin=ymin, q_xmax=xmax, q_ymax=ymax, result=[])
                node = tree.linear_BRC(q_xmin=xmin, q_ymin=ymin, q_xmax=xmax, q_ymax=ymax)

            if i == 0 and path != None:          # I feel like if I didn't use pandas, or atleast used it at the end to write to the csv file, this would possibly go faster
                #make these switch statements
                if small == True:
                    if SRC == True:
                        temp = pd.DataFrame([[[xmin,ymin,xmax,ymax],node.depth,node.bbox,node.data_size]], columns=["SRC Query: Small","Depth","BBoxes","Data Size"], index=None)
                    elif BRC == True:
                        temp = pd.DataFrame([[[xmin,ymin,xmax,ymax],node,len(node)]], columns=["BRC Query: Small","Points","# Of Points"], index=None)
                elif medium == True:
                    if SRC == True:
                        temp = pd.DataFrame([[[xmin,ymin,xmax,ymax],node.depth,node.bbox,node.data_size]], columns=["SRC Query: Medium","Depth","BBoxes","Data Size"], index=None)
                    elif BRC == True:
                        temp = pd.DataFrame([[[xmin,ymin,xmax,ymax],node,len(node)]], columns=["BRC Query: Medium","Points","# Of Points"], index=None)
                elif large == True:
                    if SRC == True:
                        temp = pd.DataFrame([[[xmin,ymin,xmax,ymax],node.depth,node.bbox,node.data_size]], columns=["SRC Query: Large","Depth","BBoxes","Data Size"], index=None)
                    elif BRC == True:
                        temp = pd.DataFrame([[[xmin,ymin,xmax,ymax],node,len(node)]], columns=["BRC Query: Large","Points","# Of Points"], index=None)
                else:
                    if SRC == True:
                        temp = pd.DataFrame([[[xmin,ymin,xmax,ymax],node.depth,node.bbox,node.data_size]], columns=["SRC Query","Depth","BBoxes","Data Size"], index=None)
                    elif BRC == True:
                        temp = pd.DataFrame([[[xmin,ymin,xmax,ymax],node,len(node)]], columns=["BRC Query","Points","# Of Points"], index=None)

            else:
                if SRC == True:
                    temp.loc[i] = [xmin,ymin,xmax,ymax],node.depth,node.bbox,node.data_size
                elif BRC == True:
                    temp.loc[i] = [xmin,ymin,xmax,ymax],node,len(node)
            if show == True:
                tree.graph_tree(plot_boxes=[[xmin,ymin,xmax,ymax]])
                # tree.graph_tree(plot_boxes=[[xmin,ymin,xmax,ymax]],middle=False)
            i+=1
    else:   #we are given a query range or a list
        #Arranges the queries xmins and ymins
        if query_list == None:
            if xmin > xmax:
                a = xmax
                xmax = xmin
                xmin = a
            if ymin > ymax:
                a = ymax
                ymax = ymin
                ymin = a
            
            #This limits the possible query ranges to the actual boundery box of the data set
            if xmin < tree.bbox[0]:
                xmin = tree.bbox[0]
            if xmax > tree.bbox[2]:
                xmax = tree.bbox[2]
            if ymin < tree.bbox[1]:
                ymin = tree.bbox[1]
            if ymax > tree.bbox[3]:
                ymax = tree.bbox[3]

        for item in query_list:
            # while i < num:      #could technically just use a length of pd.dataframe
            if SRC == True:
                node = tree.SRC(q_xmin = item[0], q_ymin = item[1], q_xmax=item[2], q_ymax=item[3])
            elif BRC == True:
                node = tree.linear_BRC(q_xmin = item[0], q_ymin = item[1], q_xmax=item[2], q_ymax=item[3])
            
            if i == 0:
                if SRC == True:
                    temp = pd.DataFrame([[[item[0],item[1],item[2],item[3]],node.depth,node.bbox,node.data_size]], columns=["SRC Query","Depth","BBoxes","Data Size"], index=None)
                elif BRC == True:
                    temp = pd.DataFrame([[[item[0],item[1],item[2],item[3]],len(node)]], columns=["BRC Query","Data Size"], index=None)       #removed "Points"
            else:   
                if SRC == True:
                    temp.loc[i] = [item[0],item[1],item[2],item[3]],node.depth,node.bbox,node.data_size
                elif BRC == True:
                    temp.loc[i] = [item[0],item[1],item[2],item[3]],len(node)
            if show == True:
                tree.graph_tree(plot_boxes=[[item[0],item[1],item[2],item[3]]])
                tree.graph_tree(plot_boxes=[[item[0],item[1],item[2],item[3]]],middle=False)
            i+=1

    if save == True:
        try:
            df = pd.read_csv(path)
            temp.to_csv(path,mode='w',index=None)
        except Exception:
            temp.to_csv(path,mode='a',columns=None,index=None)
    else:
        return print(temp)
    

def SRC_vs_BRC(tree=None,num=1,sprout=None,path=None,show=False,one_file=False,duplicates=False):
    '''
    :param tree: The 3DAG Tree.
    :param num: The number of queries that you want. Note that 1 query is 6 in total.
    :param sprout: The seed for randomness. It is required.
    :param path: This should be the local path to the Saved Query folder with the dataset query folder in it, it should look like: "Saved Query/3DAG SRC vs BRC/CRAWDAD spitz and Cali/". This method makes the rest of the folders, based on sprout and num. In a perfect world, each query set should be located in a folder labeled: sprout - num, so it would look like 1 - 100,000.
    :param show: Boolean, if set to true it will graph the 3DAG for each query and show you a graph. HIGHLY not advised if you have a large amount of queries or a large dataset.
    :param one_file: Boolean, puts everything in 1 file. Not advised.
    :param duplicates: Required Boolean, if True it will place these queries in the "With Duplicates" folder, else it will palce the queries in the "Without Duplicates" folder.
    '''
    print("Saving Mass Query...")
    #Error checking
    if tree == None:
        return print("Need a tree.")
    if path == None:
        return print("Need path to query folder!")
    if sprout == None:
        return print("Need a sprout!")
    random.seed(sprout)
    if duplicates == None:
        return print("Need to state whether or not this tree was made with duplicate points!")
    #these make sure BRC and SRC path have a '/' at the end, it lets us access what ever is in the file
    if path[len(path)-1] != "/":
        path = path+"/"

    #Making/checking path folder for the duplicates folder
    if duplicates == True:
        duplicates = 'With Duplicates/'
    else:
        duplicates = 'Without Duplicates/'
    os.makedirs(path+duplicates,exist_ok=True)                          #makes duplicate folder
    os.makedirs(path+duplicates+f"{sprout} - {num:,}",exist_ok=True)    #makes the specific query folder

    BRC_path = path+duplicates+f"{sprout} - {num:,}/BRC.csv"
    SRC_path = path+duplicates+f"{sprout} - {num:,}/SRC.csv"


    #Setting Coeffs
    small_coeff_num = (tree.bbox[2]-tree.bbox[0])*0.04
    medium_coeff_num = (tree.bbox[2]-tree.bbox[0])*0.2
    large_coeff_num = (tree.bbox[2]-tree.bbox[0])*0.3

    smallQ_list=[]
    mediumQ_list = []
    largeQ_list = []
    i=0
    while i < num:      #could change with while num != 0
        for j in range(3):
            if j == 0:
                coeff_num = small_coeff_num
            elif j == 1:
                coeff_num = medium_coeff_num
            elif j == 2:
                coeff_num = large_coeff_num
            
            xmin = round(random.uniform(tree.bbox[0],tree.bbox[2]-coeff_num),2)
            xmax = round(random.uniform(xmin+1,xmin+coeff_num),2)
            ymin = round(random.uniform(tree.bbox[1],tree.bbox[3]-coeff_num),2)
            ymax = round(random.uniform(ymin+1,ymin+coeff_num),2)
            
            #This limits the possible query ranges to the actual boundery box of the data set
            if xmin < tree.bbox[0]:
                xmin = tree.bbox[0]
            if xmax > tree.bbox[2]:
                xmax = tree.bbox[2]
            if ymin < tree.bbox[1]:
                ymin = tree.bbox[1]
            if ymax > tree.bbox[3]:
                ymax = tree.bbox[3]  
            if ymax < tree.bbox[1]:
                ymax = tree.bbox[1]
            
            if j == 0:
                smallQ_list.append([xmin,ymin,xmax,ymax])
            elif j == 1:
                mediumQ_list.append([xmin,ymin,xmax,ymax])
            elif j == 2:
                largeQ_list.append([xmin,ymin,xmax,ymax])

            # points_list.append([xmin,ymin,xmax,ymax])
        i+=1
    print("Finished Collecting Random Samples.")
    # if SRC_path != None and BRC_path == None:
    #     save_query(tree=tree,num=1,path=SRC_path,SRC=True,save=True,show=show,query_list=points_list)
    #     save_query(tree=tree,num=1,path=SRC_path,BRC=True,save=True,show=show,query_list=points_list)
    # elif BRC_path != None and SRC_path == None:
    #     save_query(tree=tree,num=1,path=BRC_path,SRC=True,save=True,show=show,query_list=points_list)
    #     save_query(tree=tree,num=1,path=BRC_path,BRC=True,save=True,show=show,query_list=points_list)
    # else:
    #     save_query(tree=tree,num=1,path=SRC_path,SRC=True,save=True,show=show,query_list=points_list)
    #     save_query(tree=tree,num=1,path=BRC_path,BRC=True,save=True,show=show,query_list=points_list)
    if one_file == False:
        print("Starting SRC Files:")
        small_SRC_path = SRC_path[:len(SRC_path)-4] + "_small4%" + SRC_path[len(SRC_path)-4:]
        medium_SRC_path = SRC_path[:len(SRC_path)-4] + "_medium" + SRC_path[len(SRC_path)-4:]
        large_SRC_path = SRC_path[:len(SRC_path)-4] + "_large" + SRC_path[len(SRC_path)-4:]
        save_query(tree=tree,num=1,path=small_SRC_path,SRC=True,BRC=False,save=True,show=show,query_list=smallQ_list)
        print("\tSmall - Complete")
        save_query(tree=tree,num=1,path=medium_SRC_path,SRC=True,BRC=False,save=True,show=show,query_list=mediumQ_list)
        print("\tMedium - Complete")
        save_query(tree=tree,num=1,path=large_SRC_path,SRC=True,BRC=False,save=True,show=show,query_list=largeQ_list)
        print("\tLarge - Complete")
        print("Finished SRC File.")

        print("Starting BRC Files:")
        small_BRC_path = BRC_path[:len(BRC_path)-4] + "_small4%" + BRC_path[len(BRC_path)-4:]
        medium_BRC_path = BRC_path[:len(BRC_path)-4] + "_medium" + BRC_path[len(BRC_path)-4:]
        large_BRC_path = BRC_path[:len(BRC_path)-4] + "_large" + BRC_path[len(BRC_path)-4:]
        save_query(tree=tree,num=1,path=small_BRC_path,BRC=True,SRC=False,save=True,show=show,query_list=smallQ_list)
        print("\tSmall - Complete")
        save_query(tree=tree,num=1,path=medium_BRC_path,BRC=True,SRC=False,save=True,show=show,query_list=mediumQ_list)
        print("\tMedium - Complete")
        save_query(tree=tree,num=1,path=large_BRC_path,BRC=True,SRC=False,save=True,show=show,query_list=largeQ_list)
        print("\tLarge - Complete")
        print("Finished BRC File.")
    else:
        Q_list = []
        i=0
        for item in smallQ_list:
            Q_list.append(item)
            Q_list.append(mediumQ_list[i])
            Q_list.append(largeQ_list[i])
            i+=1

        print("Starting SRC File:")
        save_query(tree=tree,num=1,path=SRC_path,SRC=True,save=True,show=show,query_list=Q_list)
        print("\tSRC File - Completed\nStarting BRC File:")
        save_query(tree=tree,num=1,path=BRC_path,BRC=True,save=True,show=show,query_list=Q_list)
        print("\tBRC File - Completed")


def statistics(file_path=None,graph=False):
    '''
    F/P% is found by (SRC Size/BRC Size)
    Error % is found by (BRC Size / SRC Size)*100

    When calculating the average F/P % we remove values that are inf, the # of inf values we removed is recorded in the summary.txt file in report as "Tot # of Inf".
    The F/P % is suppose to represent how incorrect our SRC search size is, compared to our BRC search size.
    '''
    if file_path == None:
        return print("We need a path!")
    print("Starting Statistics...")
    
    if file_path[len(file_path)-1] != "/":
        file_path = file_path+"/"

    small = []
    medium = []
    large = []
    #this gets all csv files of BRC and SRC, the first listed file every time will be BRC and the second will be SRC
    for item in os.listdir(file_path):
        if item.__contains__("small4%"):
            small.append(item)
        elif item.__contains__("medium"):
            medium.append(item)
        elif item.__contains__("large"):
            large.append(item)
    
    #makes report folder if it doesn't exist
    os.makedirs(f"{file_path}_Report", exist_ok=True)
    #reading from lists made earlier
    small_dataframe = pd.DataFrame(columns=['BRC Size','SRC Size','SRC Depth','Diff','F/P %','Error %'])
    small_dataframe['BRC Size'] = pd.read_csv(file_path+'/'+small[0])['Data Size']
    small_dataframe['SRC Size'] = pd.read_csv(file_path+'/'+small[1])['Data Size']
    small_dataframe['SRC Depth']=pd.read_csv(file_path+'/'+small[1])['Depth']
    small_dataframe['Error %'] = ((small_dataframe['BRC Size']/ small_dataframe['SRC Size']))*100
    small_dataframe['F/P %'] = (small_dataframe['SRC Size'] / small_dataframe['BRC Size'])
    # small_dataframe['F/P %'] = ((small_dataframe['SRC Size'] - small_dataframe['BRC Size'])/ small_dataframe['BRC Size'])*100
    small_dataframe['Diff'] = small_dataframe['SRC Size'] - small_dataframe['BRC Size']

    #change inf values to 100% for Error %
    small_dataframe['Error %'] = small_dataframe['Error %'].replace([np.inf,-np.inf],100)
    #get num of inf in F/P %
    small_total_inf = np.isinf(small_dataframe['F/P %']).values.sum()
    
    # output_path = path[:path.rfind('/')+1]+"Report small "+path[path.rfind('/')+1:]+".txt"
    small_dataframe.to_csv(file_path[:file_path.rfind('/')+1]+"_Report/small4%"+file_path[file_path.rfind('/')+1:]+".csv")


    medium_dataframe = pd.DataFrame(columns=['BRC Size','SRC Size','Diff','F/P %', 'Error %'])
    medium_dataframe['BRC Size'] = pd.read_csv(file_path+'/'+medium[0])['Data Size']
    medium_dataframe['SRC Size'] = pd.read_csv(file_path+'/'+medium[1])['Data Size']
    medium_dataframe['SRC Depth']=pd.read_csv(file_path+'/'+medium[1])['Depth']
    medium_dataframe['Error %'] =  ((medium_dataframe['BRC Size'] / medium_dataframe['SRC Size']))*100
    medium_dataframe['F/P %'] = (medium_dataframe['SRC Size'] / medium_dataframe['BRC Size'])
    # medium_dataframe['F/P %'] = ((medium_dataframe['SRC Size'] - medium_dataframe['BRC Size'])/ medium_dataframe['BRC Size'])*100
    medium_dataframe['Diff'] = medium_dataframe['SRC Size'] - medium_dataframe['BRC Size']

    #change inf values to 100% for Error %
    medium_dataframe['Error %'] = medium_dataframe['Error %'].replace([np.inf,-np.inf],100)
    #get num of inf in F/P %
    medium_total_inf = np.isinf(medium_dataframe['F/P %']).values.sum()
    
    
    # output_path = path[:path.rfind('/')+1]+"Report small "+path[path.rfind('/')+1:]+".txt"
    medium_dataframe.to_csv(file_path[:file_path.rfind('/')+1]+"_Report/medium"+file_path[file_path.rfind('/')+1:]+".csv")

    large_dataframe = pd.DataFrame(columns=['BRC Size','SRC Size','Diff','F/P %'])
    large_dataframe['BRC Size'] = pd.read_csv(file_path+'/'+large[0])['Data Size']
    large_dataframe['SRC Size'] = pd.read_csv(file_path+'/'+large[1])['Data Size']
    large_dataframe['SRC Depth']=pd.read_csv(file_path+'/'+large[1])['Depth']
    large_dataframe['Error %'] = ((large_dataframe['BRC Size'] / large_dataframe['SRC Size']))*100
    large_dataframe['F/P %'] = (large_dataframe['SRC Size'] / large_dataframe['BRC Size'])
    # large_dataframe['F/P %'] = ((large_dataframe['SRC Size'] - large_dataframe['BRC Size'])/ large_dataframe['BRC Size'])*100
    large_dataframe['Diff'] = large_dataframe['SRC Size'] - large_dataframe['BRC Size']

    #change inf values to 100% for Error %
    large_dataframe['Error %'] = large_dataframe['Error %'].replace([np.inf,-np.inf],100)
    #get num of inf in F/P %
    large_total_inf = np.isinf(large_dataframe['F/P %']).values.sum()

    # output_path = path[:path.rfind('/')+1]+"Report small "+path[path.rfind('/')+1:]+".txt"
    large_dataframe.to_csv(file_path[:file_path.rfind('/')+1]+"_Report/large"+file_path[file_path.rfind('/')+1:]+".csv")
    


    ### This is for summary ###
    #for avg BRC Size
    small_avg_BRC_size = round(small_dataframe['BRC Size'].mean(),2)
    medium_avg_BRC_size = round(medium_dataframe['BRC Size'].mean(),2)
    large_avg_BRC_size = round(large_dataframe['BRC Size'].mean(),2)

    #for avg SRC Size
    small_avg_SRC_size = round(small_dataframe['SRC Size'].mean(),2)
    medium_avg_SRC_size = round(medium_dataframe['SRC Size'].mean(),2)
    large_avg_SRC_size = round(large_dataframe['SRC Size'].mean(),2)

    #for avg SRC Depth
    small_avg_SRC_depth = round(small_dataframe['SRC Depth'].mean(),2)
    medium_avg_SRC_depth = round(medium_dataframe['SRC Depth'].mean(),2)
    large_avg_SRC_depth = round(large_dataframe['SRC Depth'].mean(),2)

    #for avg diff SRC
    small_avg_diff = round(small_dataframe['Diff'].mean(),2)
    medium_avg_diff = round(medium_dataframe['Diff'].mean(),2)
    large_avg_diff = round(large_dataframe['Diff'].mean(),2)

    #for avg F/P% (false positive rate (in percentage))
    small_avg_fp = round(small_dataframe.replace([np.inf, -np.inf],np.nan).dropna()['F/P %'].mean(),2)
    medium_avg_fp = round(medium_dataframe.replace([np.inf, -np.inf],np.nan).dropna()['F/P %'].mean(),2)
    large_avg_fp = round(large_dataframe.replace([np.inf, -np.inf],np.nan).dropna()['F/P %'].mean(),2)

    #for avg Error %
    small_avg_error = round(small_dataframe['Error %'].mean(),2)
    medium_avg_error = round(medium_dataframe['Error %'].mean(),2)
    large_avg_error = round(large_dataframe['Error %'].mean(),2)

    #for avg L2 distance (Euclidean Distance), L2 Norm
    #Question, what exactly are we applying this to? All resources I've seen are about 2 points, my guess is
    #that you would want me to apply this is every point against every point? Almost like a PCA??

    #Question 2, would this only entail me taking the L2 norm of my data?



    #writing all average info to txt file
    with open((file_path + "/_Report/Summary.txt"),'w') as file:
        file.write("Averages\n")
        file.write(f"Small4%\n\tBRC Size:\t{small_avg_BRC_size:,}\n\tSRC Size:\t{small_avg_SRC_size:,}\n\tSRC Depth:\t{small_avg_SRC_depth:,}\n\tDiff:\t\t{small_avg_diff:,}\n\tF/P %:\t\t{small_avg_fp:,}%\n\tError %:\t\t{small_avg_error:,}%\n\tTot # of Inf: {small_total_inf:,}\n\n\n")
        file.write(f"Medium\n\tBRC Size:\t{medium_avg_BRC_size:,}\n\tSRC Size:\t{medium_avg_SRC_size:,}\n\tSRC Depth:\t{medium_avg_SRC_depth:,}\n\tDiff:\t\t{medium_avg_diff:,}\n\tF/P %:\t\t{medium_avg_fp:,}%\n\tError %:\t\t{medium_avg_error:,}%\n\tTot # of Inf: {medium_total_inf:,}\n\n\n")
        file.write(f"Large\n\tBRC Size:\t{large_avg_BRC_size:,}\n\tSRC Size:\t{large_avg_SRC_size:,}\n\tSRC Depth:\t{large_avg_SRC_depth:,}\n\tDiff:\t\t{large_avg_diff:,}\n\tF/P %:\t\t{large_avg_fp:,}%\n\tError %:\t\t{large_avg_error:,}%\n\tTot # of Inf: {large_total_inf:,}\n\n\n")
        file.write("Note: Calculating the F/P% we removed queries that resulted in an inf value, we did not do this to the average BRC or SRC size.\nNote 2: Tot # of Inf is the number of BRC searches that returned 0.")
        file.close()
    
    if graph == True:
        stat_graph(file_path)

    print("Finished Statistics\n")


#does not work as of right now
def save_tree(tree,path=None):      #in future store additional information
    """
    Saves KD Tree data points in 2 columns. Data is saved in a csv file in Saved KD Trees, if no folder exists it will make one. Uses Pandas lib.
    
    :param tree: The KD Tree
    :param path: Optional path, need r before path string
    """
    if path == None:
        if os.listdir('.').__contains__("Saved KD Trees") == False and os.listdir('.').__contains__("Saved KD Tree") == False:
            os.mkdir("Saved KD Trees")
        path = f"Saved KD Trees/temp {len(os.listdir('Saved KD Trees'))+1}.csv"

    df = pd.DataFrame((tree.points),index=None)
    df.to_csv(path,index=False,header=False)


def points_from_file(path=None,columns=None,file_extension=None,drop_duplicates=False):        #Need to make it where it can split the csv file with delimeter = ' ' or ','. Also make method to work with .txt
    """
    Reads csv file and returns data in a list (which can straight forward be used in making a KD Tree). Uses Pandas lib.

    :param path: Need path (also needs r before path string)
    :param drop_duplicates: Boolean, if True it will remove all duplicate points and return a list.
    """
    if path == None:
        return print("Need path!")
    if file_extension == 'csv':
        points = pd.read_csv(path)
        # points = points.dropna(how='any')
    elif file_extension == 'excel':
        points = pd.read_excel(path)
    else:
        points = pd.read_csv(path)
        # points = points.dropna(how='any')

    if columns != None:
        points = points[columns]
        if file_extension=='csv':
            points = points.dropna()

    if drop_duplicates == True:
        points = points.drop_duplicates()

    points = points.values.tolist()
    return points


def stat_graph(path=None,title=""):
    '''
    Need to input folder path, this will graph the SRC Depth files in the folder.
    This will look at the SRC_large.csv, then SRC_medium.csv, then SRC_small.csv.
    '''
    print("Starting Statistics Graphing...")
    if path == None:
        return print("Need path!")
    if path[len(path)-1] != "/":
        path = path+"/"
    os.makedirs(f"{path}_Graphs", exist_ok=True)     #makes Graphs folder if one isn't already made
    
    if title != "":
        title = f": {title}"

    files = os.listdir(path)
    for csv_file in files:
        if csv_file.__contains__("SRC"):        #only gets csv files that are SRC Query, then gets the SRC Query.csv file's Depth, and then graphs it
            src_data = pd.read_csv((path+f"{csv_file}"))
            # src_depth = src_data['Depth']
            total_num = len(src_data['Depth'])  #normally should be 100,0000
            
            i=0     #this is to find how many times a depth is returned by SRC from the SRC Query.csv file, note it may not return the maximum depth if the SRC Query.csv file
            value_list = []
            percent_list = []
            for item in range(src_data['Depth'].max()+1):
                value_list.append(src_data['Depth'].value_counts().get(i, 0))
                percent_list.append(f"{round(((value_list[i]/total_num)*100), 2)} %")
                i+=1
            #this gets the depth of nodes returned 
            x_cord = []
            for j in range(len(value_list)):
                x_cord.append(j)

        
            ###maybe include something that gets the leaf nodes then checks all leaf nodes depth, gets max depth, and list it in the legend of the bar graph

            #making graph
            plt.figure(figsize=(8,8))
            bar = plt.bar(x_cord,value_list,width=0.6)
            plt.title(f"{str(csv_file).replace('.csv','')}{title}")
            # ax.bar(x_cord,value_list,width=0.6)

            #putting percentages on bars
            i=0
            for p in bar:
                width = p.get_width()
                height = p.get_height()
                x, y = p.get_xy()

                plt.text(x+width/2, y+height*1.01,percent_list[i],ha='center',weight='bold')
                i+=1
            
            plt.tight_layout()
            plt.savefig(f'{path}/_Graphs/{str(csv_file).replace('.csv','.png')}')
    print("Completed Statistics Graphing\n")


def lvl_diff_graph(DAGpath=None, KDpath=None):
    if DAGpath == None or KDpath == None:
        return print("We need path to query folder for both DAG and KD!")
    if DAGpath[len(DAGpath)-1] != "/":
        DAGpath = DAGpath+"/"
    if KDpath[len(KDpath)-1] != "/":
        KDpath = KDpath+"/"
    print("Starting Level Diff...")
    
    DAGfiles = []
    for item in os.listdir(DAGpath+"_Report/"):
        if item.__contains__('.csv'):
            DAGfiles.append(item)
    KDfiles = []
    for item in os.listdir(KDpath+"_Report/"):
        if item.__contains__('.csv'):
            KDfiles.append(item)

    os.makedirs(DAGpath+"_Graphs/Diff/",exist_ok=True)       #makes 'Diff' folder in 3DAGs 'Graph' folder if one isn't already there
    os.makedirs(KDpath+"_Graphs/Diff/",exist_ok=True)
    for k in range(len(DAGfiles)):                          #gets SRC csv files information. First it /SHOULD/ do large, then medium, then small
        DAG_data = pd.read_csv(DAGpath+"_Report/"+DAGfiles[k])['SRC Depth']
        KD_data = pd.read_csv(KDpath+"_Report/"+KDfiles[k])['SRC Depth']

       #this is to find how many times a depth is returned by SRC from the SRC Query.csv file, note it may not return the maximum depth if the SRC Query.csv file
        value_list = []
        for i in range(DAG_data.max()+1):
            value_list.append(DAG_data.value_counts().get(i, 0))
        #this gets the depth of nodes returned 
        x_cord = []
        for j in range(len(value_list)):
            x_cord.append(j)
        #in this it's going to be easier if we actually make a pandas dataframe then just subtract correct columns together
        DAG_df = pd.DataFrame([value_list],columns=x_cord)
        
        #Now fo KD Tree
        KD_data = pd.read_csv(KDpath+"_Report/"+KDfiles[k])['SRC Depth']
        #this is to find how many times a depth is returned by SRC from the SRC Query.csv file, note it may not return the maximum depth if the SRC Query.csv file
        value_list = []
        for i in range(KD_data.max()+1):
            value_list.append(KD_data.value_counts().get(i, 0))
        #this gets the depth of nodes returned 
        x_cord = []
        for j in range(len(value_list)):
            x_cord.append(j)
        KD_df = pd.DataFrame([value_list],columns=x_cord)
        diff_df = DAG_df-KD_df          #this will subtract correctly, as if 3DAG has values in 9 but KD doesn't it will place a NaN value there
        
        #Now to plot it
        diff_df.plot.bar(figsize=(8,6),position=0,table=True,xlim=0)
        
        plt.tight_layout()
        plt.savefig(f'{DAGpath}/_Graphs/Diff/{str(DAGfiles[k]).replace('.csv','.png')}')
        plt.savefig(f'{KDpath}/_Graphs/Diff/{str(KDfiles[k]).replace('.csv','.png')}')
    print("Finished Level Diff\n")


def nlvl_diff_graph(DAGpath=None, KDpath=None):
    if DAGpath == None or KDpath == None:
        return print("Need path for DAG and KD!")
    #makes sure that there is a slash at the end of the paths
    if DAGpath[len(DAGpath)-1] != '/':
        DAGpath = DAGpath + "/"
    if KDpath[len(KDpath)-1] != '/':
        KDpath = KDpath + "/"

    #gets the _Reports csv files paths, these will be read then processed for graphing
    DAGitems = []
    for item in os.listdir(DAGpath+"_Report/"):
        if item.__contains__('.csv'):
            DAGitems.append(item)
    KDitems = []
    for item in os.listdir(KDpath+"_Report/"):
        if item.__contains__('.csv'):
            KDitems.append(item)
    #these will always store the files: large - medium - small

    #need to get the number of items that show up
    for i in range(len(DAGitems)):
        DAG_df = pd.read_csv(DAGpath+"_Report/"+DAGitems[i])['SRC Depth']
        KD_df = pd.read_csv(KDpath+"_Report/"+KDitems[i])['SRC Depth']

        DAG_df = DAG_df.value_counts().sort_index()
        KD_df = KD_df.value_counts().sort_index()

        diff_df = DAG_df - KD_df
        x_cord = diff_df.index[:].tolist()
        value_list = diff_df.values[:]
        #got the values and x_cordinates ^^^

        os.makedirs(DAGpath+"_Graphs/Diff/",exist_ok=True)
        os.makedirs(KDpath+"_Graphs/Diff/",exist_ok=True)
        #gotta make sure the fodlers are actually made

        #making graph
        plt.figure(figsize=(8,8))
        plt.bar(x_cord,value_list,width=0.6)
        
        plt.title(f"{DAGpath}{str(DAGitems[i]).replace('.csv','')}")
        plt.tight_layout()
        # plt.legend()
        plt.xlim(right=x_cord[len(x_cord)-1])
        
        
        plt.savefig(f'{DAGpath}_Graphs/Diff/{str(DAGitems[i]).replace('.csv','')}_diff.png')
        plt.savefig(f'{KDpath}_Graphs/Diff/{str(KDitems[i]).replace('.csv','')}_diff.png')
       

    


def L2norm(path=None, show=False):
    if path == None:
        return print("Need query folder path!")
    #need to get data of SRC Depths and subtract it from the/a total distribution.
    print("Starting L2 Norm...")

    if path[len(path)-1] != "/":    #makes path accessable
                path = path+"/"
    os.makedirs(f"{path}_L2 Norm", exist_ok=True)    #makes L2 Norm folder
    files = os.listdir(path)
    for csv_file in files:
        if csv_file.__contains__("SRC"):        #only gets csv files that are SRC Query, then gets the SRC Query.csv file's Depth, and then graphs it
            data = pd.read_csv((path+f"{csv_file}"))    #data will be equal to each original SRC file

            i=0     #this is to find how many times a depth is returned by SRC from the SRC Query.csv file, note it may not return the maximum depth if the SRC Query.csv file
            value_list = []
            for item in range(data['Depth'].max()+1):
                value_list.append(data['Depth'].value_counts().get(i, 0))
                i+=1
            for j in range(len(value_list)):
                value_list[j] = value_list[j]/len(data['Depth'])
            #value list has the original data from SRC file
            columns_li = []
            for i in range(len(value_list)):
                columns_li.append(i)
            stored_data = pd.DataFrame(columns=['L2 Norm'])

            randomized_sample = data['Depth'].sample(n=len(data))   #randomized_sample fully randomly samples the entire data set
            #need to make columns of the first 100 points, then again for the first and next 100 (200 total), then containue
    
            #this is going through the randomly sampled data (SRC Depth) and going through it for every 100 points
            for i in range(int(len(randomized_sample)/100)):
                temp = randomized_sample.head(100*(i+1))
                temp_value_list = []
                j=0
                for item in range(randomized_sample.max()+1):   #this gets the depths of the nodes
                    temp_value_list.append(temp.value_counts().get(j, 0))
                    j+=1


                #temp_value_list has the # of returned nodes of this random sample, want %
                for j in range(len(temp_value_list)):
                    temp_value_list[j] = temp_value_list[j]/(100*(i+1))
                temp_row = []
                temp_val = 0
                for k in range(len(temp_value_list)):
                    # for j in range(len(temp_value_list[k])):
                    temp_val += ((temp_value_list[k]-value_list[k])**2)
                    # temp_row.append(((temp_value_list[k]-value_list[k])**2)**0.5)       #this is the L2 norm as: ((sample - original)^2)^1/2
                temp_row.append((temp_val)**0.5)
                stored_data.loc[len(stored_data)] = temp_row
            stored_data.to_csv(f"{path}/_L2 Norm/{csv_file}")

            #need to save figure (scatter)
            stored_data = stored_data.values.tolist()

            x=[]
            for i in range(len(stored_data)):
                x.append(i)
            plt.figure(figsize=(16,10))
            plt.scatter(x,stored_data,marker='*', color='grey')
            plt.xlabel("Distribution")
            plt.ylabel("L2 Norm Val")
            plt.ylim(bottom=0)
            plt.xlim(left=0)
            plt.title(f"{csv_file.replace('.csv','')}")
            plt.tight_layout()
            os.makedirs(path+"_L2 Norm/Pictures",exist_ok=True)
            plt.savefig(path+f"_L2 Norm/Pictures/{csv_file.replace('.csv','.png')}")
            if show == True:
                plt.show()
    print("Finished L2 Norm\n")

             
def L2norm_diff(DAGpath=None, KDpath=None, graph=False):
    if DAGpath == None or KDpath == None:
        return print("We need path to query folder for both DAG and KD!")
    if DAGpath[len(DAGpath)-1] != "/":
        DAGpath = DAGpath+"/"
    if KDpath[len(KDpath)-1] != "/":
        KDpath = KDpath+"/"
    print("Starting L2 Norm Diff...")

    DAGfiles = []
    for item in os.listdir(DAGpath+"_L2 Norm"):
        if item.__contains__('.csv'):
            DAGfiles.append(item)
    KDfiles = []
    for item in os.listdir(KDpath+"_L2 Norm"):
        if item.__contains__('.csv'):
            KDfiles.append(item)

    os.makedirs(f"{DAGpath}_L2 Norm/Diff", exist_ok=True)
    os.makedirs(f"{KDpath}_L2 Norm/Diff", exist_ok=True)
    #now need to find diff
    for i in range(len(DAGfiles)):
        #need to make dataframe based on columns of DAG file
        DAGdf = pd.read_csv(DAGpath+"_L2 Norm/"+DAGfiles[i])
        
        KDdf = pd.read_csv(KDpath+"_L2 Norm/"+KDfiles[i])

        diff_df = DAGdf - KDdf
        diff_df = diff_df['L2 Norm']        
        diff_df.to_csv(DAGpath+"_L2 Norm/Diff/"+DAGfiles[i][:len(DAGfiles[i])-4]+"_diff.csv")
        diff_df.to_csv(KDpath+"_L2 Norm/Diff/"+KDfiles[i][:len(KDfiles[i])-4]+"_diff.csv")
        # diff_df = None

        if graph == True:
            os.makedirs(f"{DAGpath}_L2 Norm/Diff/Pictures", exist_ok=True)
            os.makedirs(f"{KDpath}_L2 Norm/Diff/Pictures", exist_ok=True)
            x = []
            for j in range(len(diff_df)):
                x.append(j)

            plt.figure(figsize=(16,10))
            plt.scatter(x,diff_df,marker='*', color='grey')
            plt.xlabel("Distribution")
            plt.ylabel("L2 Norm Val")
            plt.ylim(bottom=0)
            plt.xlim(left=0)
            plt.title(f"{DAGfiles[i].replace('.csv','')}")
            plt.tight_layout()
            plt.savefig(DAGpath+f"_L2 Norm/Diff/Pictures/{DAGfiles[i].replace('.csv','.png')}")
            plt.savefig(KDpath+f"_L2 Norm/Diff/Pictures/{KDfiles[i].replace('.csv','.png')}")
    print("Finished L2 Norm Diff\n")



#This is entirly to just increase the maximum recursion depth for sorintg
# import sys
# sys.setrecursionlimit(1000) #originally is 1000

### Note ###
    #When making mass queries use SRC_vs_BRC method, just make a folder 
    #in Saved Query -> 3DAG SRC vs BRC if you are making queries on a dataset that hasn't
    #been used before. Else, just put the Saved Query -> 3DAG SRC vs BRC -> dataset folder.

    #If you use any of the extra methods, (statistics, stat_graph, lvl_diff_graph, L2norm,
    #L2norm_diff) you will need to insert the path to the specific query folder you want to run
    #this on, it would go something like: Saved Query -> 3DAG SRC vs BRC -> CRAWDAD spitz and Cali
    #-> Without Duplicates -> 1 - 100,000. 

    #If you use any of the diff methods, you will have to give the specific query folder for both
    #the 3DAG and KD Tree.



### TEST THIS ###
DAGpath = r"Saved Query/3DAG SRC vs BRC/Spatial/Without Duplicates/1 - 100,000"
KDpath = r"Saved Query/KD SRC vs BRC/Spatial/Without Duplicates/1 - 100,000"
nlvl_diff_graph(DAGpath=DAGpath, KDpath=KDpath)


# ### Spatial Database NO Duplication ###
# path = r"Saved Datasets/Spatial.xlsx"
# points = points_from_file(path,columns=['lon','lat'],file_extension='excel',drop_duplicates=True)
# #___________________________________________________________________________#




# path = r"Saved Query/3DAG SRC vs BRC/Spatial/"
# print(f"This is the length of points being inputed into the tree: {len(points)}")
# temp = DAGTree(points, cuttoff=4)
# print("Done with making tree.")

# # SRC_path = r"Saved Query/3DAG SRC vs BRC/Spatial/".format(i+2)
# SRC_vs_BRC(tree=temp,num=100000,sprout=3,one_file=False,path=path,show=False,duplicates=False)
# path = r"Saved Query/3DAG SRC vs BRC/Spatial/Without Duplicates/{} - 100,000/".format(3)
# statistics(path,graph=True)
# stat_graph(path)
# L2norm(path)
# print(f"\n\n3 Batch Done\n"+"_"*50+"\n\n")





# input("Press enter whenever ready to continue")

# DAGpath = r"Saved Query/3DAG SRC vs BRC/Spatial/Without Duplicates/{} - 100,000/".format(3)
# KDpath = r"Saved Query/KD SRC vs BRC/Spatial/Without Duplicates/{} - 100,000/".format(3)
# lvl_diff_graph(DAGpath=DAGpath,KDpath=KDpath)
# L2norm_diff(DAGpath=DAGpath,KDpath=KDpath)
# print(f"\n\n3 Batch Done For Diffs\n"+"_"*50+"\n\n")

# print("Finished With 3DAG Tree!")


















##### DATASETS #####
    #All /SHOULD/ automatically be set to drop duplicates

# ### CRAWDAD spitz/cellular Dataset Dropping Duplicates ###
# path = r"Saved Datasets/DT-mobile-data.csv/VDS_MS_310809_27_0210.csv"
# points = points_from_file(path,columns=['Laenge','Breite'],file_extension='csv',drop_duplicates=True)
# #___________________________________________________________________________#


# ### SRFG-v1 ###
# path = r"Saved Datasets/Check/SRFG-v1.csv"
# points = points_from_file(path,columns=['lat','long'],file_extension='csv',drop_duplicates=True)
# #___________________________________________________________________________#

# ### Inventory of Owned & Leased Properties (IOLP) ###
# building_path = r"Saved Datasets/Inventory of Owned and Leased Properties/2026-2-20-iolp-buildings.xlsx"
# lease_path = r"Saved Datasets/Inventory of Owned and Leased Properties/2026-2-20-iolp-leases.xlsx"

# points = points_from_file(lease_path,columns=['Latitude','Longitude'],file_extension='excel',drop_duplicates=True)
# building_points = points_from_file(building_path,columns=['Latitude','Longitude'],file_extension='excel',drop_duplicates=True)
# #_____________________________________________________________________________#



# ### Spatial Database NO Duplication ###
# path = r"Saved Datasets/Spatial.xlsx"
# points = points_from_file(path,columns=['lon','lat'],file_extension='excel',drop_duplicates=True)
# #___________________________________________________________________________#



### Template for SRC path and BRC path ###
# SRC_path = r"Saved Query/3DAG SRC vs BRC/Spatial/Without Duplicates/1 - 100,000/Spatial_SRC.csv"
# BRC_path = r"Saved Query/3DAG SRC vs BRC/Spatial/Without Duplicates/1 - 100,000/Spatial_BRC.csv"