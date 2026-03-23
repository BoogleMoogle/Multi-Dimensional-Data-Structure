import matplotlib.pyplot as plt
import random
import pandas as pd
import os
import numpy as np

#to see stack
import inspect

#to turn off future warnings
import warnings

# from pygame import SCRAP_CLIPBOARD
warnings.simplefilter(action='ignore',category=FutureWarning)





class KDTree:
    def __init__(self, points=[], depth=0, axis=0, split_value=None, bbox=[], left=None, right=None, parent=None, cuttoff=1):   #store data size
        self.left = left
        self.right = right

        self.data_size = len(points)
        self.parent = parent
        if axis == 0:   #sort by x values
            points.sort()
        else:           #sort by y values
            points.sort(key=lambda x: x[1])     #!!!If range is too short then it will crash due to number of repeating values and recursion
        self.points=points

        self.depth=depth
        self.axis=axis
        self.split_value=split_value
        self.cuttoff = cuttoff

        if len(bbox) == 0:      #only need to find bbox for first time
            self.bbox = self.find_bbox(bbox)
        else:
            self.bbox = bbox

        if self.data_size > self.cuttoff:
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
        #this is to write to a temp.txt file in recursion versions
        # with open(r"Recursion Versions/temp.txt",'a') as file:
        #     file.write(f"{len(inspect.stack())}\n")
        #     file.close()

        # print(len(inspect.stack()))
        
        

        if self.axis == 0:
            self.points.sort()
        else:
            self.points.sort(key=lambda x: x[1])
        self.split_value = self.points[len(self.points)//2]

        #Hard Splitting Method          (not ideal, but easier)
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


        if self.parent != None and self.parent.data_size == self.data_size:     #this checks if the parent's data size is the same as this nodes, if so then we need to stop. All poitns were inherited to either the left or right child (probably right)
            pass
        else:
            # if self.parent != None:
                # self.parent.points=None
            if self.axis == 0:
                self.left = KDTree(left, depth=self.depth+1, axis=1, bbox=[self.bbox[0], self.bbox[1], self.split_value[self.axis], self.bbox[3]], parent=self, cuttoff=self.cuttoff)
                self.right = KDTree(right, depth=self.depth+1, axis=1, bbox=[self.split_value[self.axis], self.bbox[1], self.bbox[2], self.bbox[3]], parent=self, cuttoff=self.cuttoff)
            else:
                self.left = KDTree(left,  depth=self.depth+1, axis=0, bbox=[self.bbox[0], self.bbox[1], self.bbox[2], self.split_value[self.axis]], parent=self, cuttoff=self.cuttoff)
                self.right = KDTree(right, depth=self.depth+1, axis=0, bbox=[self.bbox[0], self.split_value[self.axis], self.bbox[2], self.bbox[3]], parent=self, cuttoff=self.cuttoff)


    #Single Range Cover Search Method
    def SRC(self, q_xmin, q_ymin, q_xmax, q_ymax, graph=False, best=None):
        # if best == None:
        #     best = self

        if self.bbox[0] <= q_xmin and self.bbox[2] >= q_xmax and self.bbox[1] <= q_ymin and self.bbox[3] >= q_ymax: #this node 100% contains the range
            if best == None or best.depth < self.depth:
                best = self
            if self.left != None:
                if self.left.bbox[2] >= q_xmax and self.left.bbox[3] > q_ymax:      #self.bbox[q_xmin,q_ymin,q_xmax,q_ymax]
                    return self.left.SRC(q_xmin, q_ymin, q_xmax, q_ymax, best)

            if self.right != None:
                if self.right.bbox[0] <= q_xmin and self.right.bbox[1] <= q_ymin:
                    return self.right.SRC(q_xmin, q_ymin, q_xmax, q_ymax, best)
            return best
        
        # else:
        #     if self.left != None:
        #         if self.left.bbox[2] > q_xmax and self.left.bbox[3] >= q_ymax:
        #             return self.left.SRC_helper(q_xmin, q_ymin, q_xmax, q_ymax, best)
        #     if self.right != None:
        #         if self.right.bbox[0] <= q_xmin and self.right.bbox[1] <= q_ymin:
        #             return self.right.SRC_helper(q_xmin, q_ymin, q_xmax, q_ymax, best)
        


    def SRC_helper(self, q_xmin, q_ymin, q_xmax, q_ymax, best=None):
        if q_xmin > q_xmax:
            temp = q_xmax
            q_xmax = q_xmin
            q_xmin = temp
        if q_ymin > q_ymax:
            temp = q_ymax
            q_ymax = q_ymin
            q_ymin = temp

        alist = []
        if self.bbox[0] <= q_xmin and self.bbox[2] >= q_xmax and self.bbox[1] <= q_ymin and self.bbox[3] >= q_ymax: #this node 100% contains the range
            alist.append(self.left.SRC(q_xmin, q_ymin, q_xmax, q_ymax, best))
            alist.append(self.right.SRC(q_xmin, q_ymin, q_xmax, q_ymax, best))
            node = None
            for item in alist:
                if node == None or node.depth < item.depth:
                    node = item
            return node
        #need to find node that is in range
        else:
            if self.left != None:
                if self.left.bbox[2] > q_xmax and self.left.bbox[3] >= q_ymax:
                    return self.left.SRC_helper(q_xmin, q_ymin, q_xmax, q_ymax, best)
            if self.right != None:
                if self.right.bbox[0] <= q_xmin and self.right.bbox[1] <= q_ymin:
                    return self.right.SRC_helper(q_xmin, q_ymin, q_xmax, q_ymax, best)








        # # if self.split_value == None:
        # #     return self
        # if self.bbox[0] <= q_xmin and self.bbox[2] >= q_xmax and self.bbox[1] <= q_ymin and self.bbox[3] >= q_ymax: #this node 100% contains the range
        #     if best == None or best.depth < self.depth:
        #         best = self
        #     if self.axis == 1:
        #         if self.left != None and self.left.bbox[2] >= q_xmax and self.left.bbox[3] > q_ymax:      #self.bbox[q_xmin,q_ymin,q_xmax,q_ymax]
        #             return self.left.SRC(q_xmin, q_ymin, q_xmax, q_ymax, best)
        #         if self.right != None and self.right.bbox[0] <= q_xmin and self.right.bbox[1] <= q_ymin:
        #             return self.right.SRC(q_xmin, q_ymin, q_xmax, q_ymax, best)
        #     else:
        #         if self.left != None:
        #             if self.left.bbox[2] > q_xmax and self.left.bbox[3] >= q_ymax:
        #                 return self.left.SRC(q_xmin, q_ymin, q_xmax, q_ymax, best)
        #         if self.right != None:
        #             if self.right.bbox[0] <= q_xmin and self.right.bbox[1] <= q_ymin:
        #                 return self.right.SRC(q_xmin, q_ymin, q_xmax, q_ymax, best)
        #     return best
        
        # else:
        #     if self.left != None:
        #         if self.left.bbox[2] > q_xmax and self.left.bbox[3] >= q_ymax:
        #             return self.left.SRC(q_xmin, q_ymin, q_xmax, q_ymax, best)
        #     if self.right != None:
        #         if self.right.bbox[0] <= q_xmin and self.right.bbox[1] <= q_ymin:
        #             return self.right.SRC(q_xmin, q_ymin, q_xmax, q_ymax, best)
        # return best


    #BRC Searching Method
    def BRC(self, q_xmin, q_ymin, q_xmax, q_ymax, result=[]):
        if self.points != None:
            for item in self.points:
                if item[0] <= q_xmax and item[0] >= q_xmin and item[1] <= q_ymax and item[1] >= q_ymin:
                    result.append(item)
        else:
            if self.bbox[0] <= q_xmin and self.bbox[1] <= q_ymin: #if q_xmin and q_ymin are bigger than this nodes xmin and y min, we need to go right
                if self.right != None:
                    self.right.BRC(q_xmin, q_ymin, q_xmax, q_ymax, result)
                if self.left != None:
                    self.left.BRC(q_xmin, q_ymin, q_xmax, q_ymax, result)
            else:   #we need to go left
                if self.left != None:
                    self.left.BRC(q_xmin, q_ymin, q_xmax, q_ymax, result)
        return result


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


    #Get Leaf Method - Just returns a list of leaf nodes (being the points)
    def get_leaf_linear(self,boxes=[]):
        if self.points != None:
            boxes.append(self.points)
        if self.left != None:
            self.left.get_leaf_linear(boxes)
        if self.right != None:
            self.right.get_leaf_linear(boxes)
        return boxes


    #Graph Tree Function
    def graph_tree(self,plot_boxes=None):

        x = []
        y = []
        boxes = self.get_leaf()

        for item in boxes:
            for point in item[3]:
                if point[0] == None or point[1] == None:
                    pass
                else:
                    x.append(point[0])
                    y.append(point[1])
        plt.scatter(x, y, c='grey', marker='o')
 
        plt.vlines(x=self.bbox[2],ymin=self.bbox[1],ymax=self.bbox[3],linestyles=':')
        plt.vlines(x=self.bbox[0],ymin=self.bbox[1],ymax=self.bbox[3],linestyles=':')
        plt.hlines(y=self.bbox[3],xmin=self.bbox[0],xmax=self.bbox[2],color='red',linestyles=':')
        plt.hlines(y=self.bbox[1],xmin=self.bbox[0],xmax=self.bbox[2],color='red',linestyles=':')
        
        boxes = self.itterate_through(leaf=False)
        # for item in boxes:
            # print(item[2])
        for item in boxes:
            if item[0] == 0:
                plt.vlines(x=item[2],ymin=item[1][1],ymax=item[1][3],linestyles=':')

            elif item[0] == 1:
                    plt.hlines(y=item[2],xmin=item[1][0],xmax=item[1][2],color='red',linestyles=':',label=f"Y = {item[2]}")

        if plot_boxes != None:
            for item in plot_boxes:
                plt.hlines(y=item[1], xmin=item[0], xmax=item[2], color='green')
                plt.hlines(y=item[3], xmin=item[0], xmax=item[2], color='green')

                plt.vlines(x=item[0], ymin=item[1], ymax=item[3], color='green')
                plt.vlines(x=item[2], ymin=item[1], ymax=item[3], color='green')

        plt.tight_layout()
        plt.show()


        #Get Leaf Method - Just returns a list of leaf nodes (being the points)


    def get_leaf(self,boxes=[]):
        if self.left == None:
            boxes.append([self.axis,self.bbox,self.depth,self.points])
        
        if self.left != None:
            self.left.get_leaf(boxes)
        if self.right != None:
            self.right.get_leaf(boxes)
        return boxes


    #Itteratting Through KDTree Function
    def itterate_through(self,boxes=[],leaf=False):
        '''
        Returns [self.axis, self.bbox, self.split_value[self.axis], and self.depth, self.points] in that order
        
        :param self: Description
        :param boxes: Description
        :param leaf: If True will return only the leaf nodes of KDTree
        '''
        # print(self)
        if leaf == True:
            return self.get_leaf()
        
        if self.split_value != None:
            boxes.append([self.axis,self.bbox,self.split_value[self.axis],self.depth,self.points])  #removed self.parent

        
        if self.left != None:
            self.left.itterate_through(boxes)
        if self.right != None:
            self.right.itterate_through(boxes)
        

        return boxes


    #Print Tree Function        -- Want me to add the range of each node (range - x,y min and max values)
    def print_tree(self,sort=False,whole=False,path=None):
        temp = []
        if whole == False:
            data = self.itterate_through()
        else:
            data = self.itterate_through(leaf=True)
            self.print_tree(whole=False,sort=sort)

        for item in data:
            if item[0] == 0:    #x axis
                temp.append([item[3],item[2],0,item[1]])
            else:               #y axis
                temp.append([item[3],item[2],1,item[1]])
        if sort == True:
            temp.sort()
        
        if path != None:
            with open(path,'a') as file:
                file.write("| Depth\t\t| Split Node:\t\t| Range: [xmin, xmax] [ymin, ymax]\n")
                for item in temp:
                    if type(item[0]) == list:
                        file.write(f"| Depth: {item[1]}\t| Data: {item[0]}\t\t| Range: [{item[3][0]}, {item[3][2]}] [{item[3][1]}, {item[3][3]}]\n")
                    elif item[2] == 0:
                        file.write(f"| Depth: {item[0]}\t| X = {item[1]}\t\t| Range: [{item[3][0]}, {item[3][2]}] [{item[3][1]}, {item[3][3]}]\n")
                    else:
                        file.write(f"| Depth: {item[0]}\t| Y = {item[1]}\t\t| Range: [{item[3][0]}, {item[3][2]}] [{item[3][1]}, {item[3][3]}]\n")
                file.close()
        else:
            print("| Depth\t\t| Split Node:\t\t| Range: [xmin, xmax] [ymin, ymax]")
            for item in temp:
                if type(item[0]) == list:
                    print(f"| Depth: {item[1]}\t| Data: {item[0]}\t\t| Range: [{item[3][0]}, {item[3][2]}] [{item[3][1]}, {item[3][3]}]")
                elif item[2] == 0:
                    print(f"| Depth: {item[0]}\t| X = {item[1]}\t\t| Range: [{item[3][0]}, {item[3][2]}] [{item[3][1]}, {item[3][3]}]")
                else:
                    print(f"| Depth: {item[0]}\t| Y = {item[1]}\t\t| Range: [{item[3][0]}, {item[3][2]}] [{item[3][1]}, {item[3][3]}]")





###### General Use Methods ######
def make_points(num=1, sprout=None, aRang=0, bRang=100):
    temp = []
    if sprout != None:
        random.seed(sprout)
    while len(temp) < num:
        temp.append((random.randint(aRang,bRang),random.randint(aRang,bRang)))
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


def points_from_file(path=None,columns=None,file_extension=None,drop_duplicates=False):        #Need to make it where it can split the csv file with delimeter = ' ' or ','. Also make method to work with .txt
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


def SRC_vs_BRC(tree=None,num=1,sprout=None,path=None,show=False,duplicates=False,starting_per=.30,interval=None):
    '''
    :param tree: The 3DAG Tree.
    :param num: The number of queries that you want. Note that 1 query is 6 in total.
    :param sprout: The seed for randomness. It is required.
    :param path: This should be the local path to the Saved Query folder with the dataset query folder in it, it should look like: "Saved Query/3DAG SRC vs BRC/CRAWDAD spitz and Cali/". This method makes the rest of the folders, based on sprout and num. In a perfect world, each query set should be located in a folder labeled: sprout - num, so it would look like 1 - 100,000.
    :param show: Boolean, if set to true it will graph the 3DAG for each query and show you a graph. HIGHLY not advised if you have a large amount of queries or a large dataset.
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

    coeffs_list = []
    #Setting Coeffs
    for j in range(int(round((starting_per*100) / interval,0))+1):
        coeffs_list.append(((starting_per*100) -(interval*(j)))/100)
    #we have coefficents list, now we need to make a csv file for every item in it

    for i in range(len(coeffs_list)):
        if coeffs_list[i] <= 0:
            coeffs_list.remove(coeffs_list[i])
            break
        coeff_num = (tree.bbox[2]-tree.bbox[0])*coeffs_list[i]
        points_list = []
        # BRC_path = path+"BRC.csv"
        # SRC_path = path+"SRC.csv"
        j=0
        while j != num:
            xmin = round(random.uniform(tree.bbox[0],tree.bbox[2]-coeff_num),2)
            xmax = round(random.uniform(xmin+1,xmin+coeff_num),2)
            ymin = round(random.uniform(tree.bbox[1],tree.bbox[3]-coeff_num),2)
            ymax = round(random.uniform(ymin+1,ymin+coeff_num),2)

            #checking for incorrect mins and maxs
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
            
            # print(f"{xmin},{ymin},{xmax},{ymax}")
            points_list.append([xmin,ymin,xmax,ymax])
            j+=1
        
        # for j in range(len(points_list)):
        print("Starting SRC Files...")
        SRC_path = f"{path}SRC_{coeffs_list[i]:.2f}.csv"
        print(f"Starting SRC at {coeffs_list[i]:.2f}...")
        save_query(tree=tree,num=1,path=SRC_path,SRC=True,BRC=False,save=True,show=show,query_list=points_list)
        print(f"Finished SRC at {coeffs_list[i]:.2f}")
            
        BRC_path = f"{path}BRC_{coeffs_list[i]:.2f}.csv"
        print(f"\nStarting BRC at {coeffs_list[i]:.2f}...")
        save_query(tree=tree,num=1,path=BRC_path,SRC=False,BRC=True,save=True,show=show,query_list=points_list)
        print(f"Finished BRC at {coeffs_list[i]:.2f}\n")
    print("\nFinished SRC and BRC Queries\n")


def statistics(file_path=None,graph=False,show=False):
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

    os.makedirs(file_path+"_Report/", exist_ok=True)

    for item  in os.listdir(file_path):
        df = pd.DataFrame(columns=['BRC Size','SRC Size','SRC Depth','Diff','F/P %','Error %'])
        if item.__contains__('.csv') and item.__contains__('BRC'):
            df['BRC Size'] = pd.read_csv(file_path + item)['Data Size']
            df['SRC Size'] = pd.read_csv(file_path + item.replace('BRC','SRC'))['Data Size']
            df['SRC Depth'] = pd.read_csv(file_path + item.replace('BRC','SRC'))['Depth']
            df['Error %'] = ((df['BRC Size']/df['SRC Size']))*100
            df['F/P %'] = (df['SRC Size']/df['BRC Size'])
            df['Diff'] = df['SRC Size'] - df['BRC Size']
            #change inf values to 100% for Error %
            df['Error %'] = df['Error %'].replace([np.inf,-np.inf],100)
            #get num of inf in F/P %
            df_total_inf = np.isinf(df['F/P %']).values.sum()
            df.to_csv(file_path+f"_Report/{item.replace('BRC_','')}")

            #this is for summary
            df_avg_BRC_size = round(df['BRC Size'].mean(),2)
            df_avg_SRC_size = round(df['SRC Size'].mean(),2)
            df_avg_SRC_depth = round(df['SRC Depth'].mean(),2)
            df_avg_diff = round(df['Diff'].mean(),2)
            df_avg_fp = round(df.replace([np.inf, -np.inf],np.nan).dropna()['F/P %'].mean(),2)
            df_avg_error = round(df['Error %'].mean(),2)

            with open(file_path+"_Report/_Summary.txt", 'a') as file:
                file.write(f"{item.replace('BRC_','').replace('.csv','')}\n\tBRC Size:\t{df_avg_BRC_size:,}\n\tSRC Size:\t{df_avg_SRC_size:,}\n\tSRC Depth:\t{df_avg_SRC_depth:,}\n\tDiff:\t\t{df_avg_diff:,}\n\tF/P %:\t\t{df_avg_fp:,}%\n\tError %:\t\t{df_avg_error:,}%\n\tTot # of Inf: {df_total_inf:,}\n\n\n")
            if graph == True:
                stat_graph(file_path,show=show)
    print("Finished Statistics\n")


def stat_graph(path=None,title="",show=False):
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
            if show == False:
                plt.close()
            else:
                plt.show()
    print("Completed Statistics Graphing\n")


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
            for i in range(int(randomized_sample.shape[0]/100)):
                temp = randomized_sample.head(100*(i+1))
                temp_value_list = []

                for j in range(randomized_sample.max()+1):   #this gets the depths of the nodes
                    temp_value_list.append(temp.value_counts().get(j, 0))

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




# To increase recursive stack frame amount
# import sys
# sys.setrecursionlimit(2090000000) #originally is 1000


### TEST THIS ###

















### TEMPLATE TO DO EVERYTHING ###


### Spatial Database NO Duplication ###
path = r"Saved Datasets/Spatial.xlsx"
points = points_from_file(path,columns=['lon','lat'],file_extension='excel',drop_duplicates=True)
#___________________________________________________________________________#


print(f"This is the length of points being inputed into the tree: {len(points)}")
temp = KDTree(points, cuttoff=4)
print("Done with making tree.")

num = 500000
sprout = 1
dataset ="Spatial"
os.makedirs(f"Saved Query/{dataset}/", exist_ok=True)
dup = False
itterations = 1
interval = 4
starting_per = 0.06

if dup == False:
    dup = "Without Duplicates"
else:
    dup = "With Duplicates"

for i in range(itterations):
    os.makedirs(r"Saved Query/KD SRC vs BRC/{}/{}".format(dataset,dup), exist_ok=True)
    path = r"Saved Query/KD SRC vs BRC/{}/{}/{} - {}/".format(dataset,dup,(sprout+i),f"{num:,}")
    os.makedirs(path,exist_ok=True)
    SRC_vs_BRC(tree=temp,num=num,sprout=sprout+i,path=path,show=False,duplicates=False,starting_per=starting_per,interval=interval)

    statistics(path,graph=True)
    L2norm(path)
print("KDTree done!!\n"+"_"*50)

###############################################################################









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
# SRC_path = r"Saved Query/3DAG SRC vs BRC/Spatial/"
# BRC_path = r"Saved Query/3DAG SRC vs BRC/Spatial/"



