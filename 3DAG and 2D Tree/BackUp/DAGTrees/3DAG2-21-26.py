from matplotlib.lines import lineStyles
import matplotlib.pyplot as plt
import random
import pandas as pd
import os
from math import ceil
from shapely import box

#to see stack
import inspect




class KDTree:
    def __init__(self, points=[], depth=0, axis=0, split_value=None, bbox=[], left=None, right=None, middle_child=False, parent=None):
        self.left = left
        self.right = right
        self.middle = middle_child
        self.parent = parent
        self.data_size = len(points)
        self.middle_child = middle_child

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

        if self.parent == None:
            self.split_value = self.points[len(self.points)//2][0]
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
        # print("Split!!!")
        # print(len(inspect.stack()))
        if self.points != None:
            #Points need to be sorted before being put in the left or right or middle child
            if self.axis == 0:
                self.points.sort()
            else:
                self.points.sort(key=lambda x: x[1])
            
            self.split_value = self.points[len(self.points)//2]

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
                if item[self.axis] <= right[len(right)//2][self.axis]:
                    if item[self.axis] == right[len(right)//2][self.axis]:              #need to check secondary values still
                        if item[(self.axis + 1) % 2] <= right[len(right)//2][(self.axis + 1) % 2]:
                            middle.append(item)
                    else:
                        middle.append(item)


            # # self.points = None
            # if self.parent != None and self.parent.data_size == self.data_size:     #this checks if the parent's data size is the same as this nodes, if so then we need to stop. All poitns were inherited to either the left or right child (probably right)
            #     pass
            else:
                if self.axis == 0:  #this is on the x axis
                    self.left = KDTree(left, depth=self.depth+1, axis=1, bbox=[self.bbox[0], self.bbox[1], self.split_value[self.axis], self.bbox[3]], parent=self)
                    self.right = KDTree(right, depth=self.depth+1, axis=1, bbox=[self.split_value[self.axis], self.bbox[1], self.bbox[2], self.bbox[3]], parent=self)
                    if middle != []:
                        self.middle = KDTree(middle, depth=self.depth+1, axis=1, bbox=[middle[0][0],self.bbox[1],middle[len(middle)-1][0],self.bbox[3]], parent=self, middle_child=True)
                else:               #this is on the y axis
                    self.left = KDTree(left,  depth=self.depth+1, axis=0, bbox=[self.bbox[0], self.bbox[1], self.bbox[2], self.split_value[self.axis]], parent=self)
                    self.right = KDTree(right, depth=self.depth+1, axis=0, bbox=[self.bbox[0], self.split_value[self.axis], self.bbox[2], self.bbox[3]], parent=self)
                    if middle != []:
                        self.middle = KDTree(middle, depth=self.depth+1, axis=0, bbox=[self.bbox[0],middle[0][1],self.bbox[2],middle[len(middle)-1][1]], parent=self, middle_child=True)

                if self.left.bbox == self.middle.bbox:
                    # with open(r"OH MY GOD IT HAPPEND.txt", 'a') as file:
                    #     file.write("OH MY GOD IT HAPPENED FOR A LEFT\n")                  ([12,12),(12,12),(12,12)])      ([12,12),(12,12),(12,12)])          ([12,12),(12,12),(12,12)])
                    #     file.close
                    self.middle=self.left
        
                if self.right.bbox == self.middle.bbox:
                    # with open(r"OH MY GOD IT HAPPEND.txt", 'a') as file:
                    #     file.write("OH MY GOD IT HAPPENED FOR A RIGHT\n")
                    #     file.close
                    self.middle=self.right

                if self.left.data_size > 4:
                    self.left.split()
                if self.right.data_size > 4:
                    self.right.split()
                if self.middle.data_size > 4:
                    self.middle.split()
                    # self.middle.split_value=None


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
            
        if self.split_value == None:
            return self
        if self.bbox[0] <= q_xmin and self.bbox[2] >= q_xmax and self.bbox[1] <= q_ymin and self.bbox[3] >= q_ymax: #this node 100% contains the range
            if self.axis == 1:
                if self.middle.bbox[0] <= q_xmin and self.middle.bbox[2] >= q_xmax and self.middle.bbox[1] <= q_ymin and self.middle.bbox[3] >= q_ymax:     #we want to go down the middle first because it has the widest search
                    return self.middle.SRC(q_xmin, q_ymin, q_xmax, q_ymax)
                elif self.left.bbox[2] >= q_xmax and self.left.bbox[3] > q_ymax:      #self.bbox[q_xmin,q_ymin,q_xmax,q_ymax]
                    return self.left.SRC(q_xmin, q_ymin, q_xmax, q_ymax)
                elif self.right.bbox[0] <= q_xmin and self.right.bbox[1] <= q_ymin:
                    return self.right.SRC(q_xmin, q_ymin, q_xmax, q_ymax)
                
            else:
                if self.middle.bbox[0] <= q_xmin and self.middle.bbox[2] >= q_xmax and self.middle.bbox[1] <= q_ymin and self.middle.bbox[3] >= q_ymax:
                    return self.middle.SRC(q_xmin, q_ymin, q_xmax, q_ymax)
                if self.left.bbox[2] > q_xmax and self.left.bbox[3] >= q_ymax:
                    return self.left.SRC(q_xmin, q_ymin, q_xmax, q_ymax)
                elif self.right.bbox[0] <= q_xmin and self.right.bbox[1] <= q_ymin:
                    return self.right.SRC(q_xmin, q_ymin, q_xmax, q_ymax)
        else:
            return self
        return self



    def BRC(self, q_xmin, q_ymin, q_xmax, q_ymax, result=[]):
        # print(self)
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


    #Graph Tree Function
    def graph_tree(self,plot_boxes=None):
        x = []
        y = []
        boxes = self.get_leaf()    #gives: axis, bbox, depth, points

        for item in boxes:
            for point in item[3]:
                if point[0] == None or point[1] == None:
                    pass
                else:
                    x.append(point[0])
                    y.append(point[1])
        plt.scatter(x, y, c='grey', marker='o')
 
        plt.vlines(x=self.bbox[2],ymin=self.bbox[1],ymax=self.bbox[3],color='blue',linestyles=':')
        plt.vlines(x=self.bbox[0],ymin=self.bbox[1],ymax=self.bbox[3],color='blue',linestyles=':')
        plt.hlines(y=self.bbox[3],xmin=self.bbox[0],xmax=self.bbox[2],color='red',linestyles=':')
        plt.hlines(y=self.bbox[1],xmin=self.bbox[0],xmax=self.bbox[2],color='red',linestyles=':')

        boxes = self.itterate_through()   #give: axis, bbox, split_value[self.axis], depth, points
        for item in boxes:
            if item[5] == True:
                if item[0] == 1:    #plot middle for x
                    # plt.fill_between(x=item[1][1],y1=item[1][1],y2=item[1][3])
                    plt.vlines(x=item[1][0]-0.1,ymin=item[1][1],ymax=item[1][3],color='purple',linestyles='-.')
                    plt.vlines(x=item[1][2]-0.1,ymin=item[1][1],ymax=item[1][3],color='purple',linestyles='-.')
                else:               #plot middle for y
                    plt.hlines(y=item[1][1]-0.1,xmin=item[1][0],xmax=item[1][2],color='brown',linestyles='-.')
                    plt.hlines(y=item[1][3]-0.1,xmin=item[1][0],xmax=item[1][2],color='brown',linestyles='-.')

            elif item[0] == 0:
                plt.vlines(x=item[2],ymin=item[1][1],ymax=item[1][3],color='blue',linestyles=':')

            elif item[0] == 1:
                plt.hlines(y=item[2],xmin=item[1][0],xmax=item[1][2],color='red',linestyles=':')

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
        '''
        if leaf==True:
            return self.get_leaf()

        if self.split_value == None:
            boxes.append([self.axis,self.bbox,self.split_value,self.depth,self.points,self.middle_child])
        else:
            boxes.append([self.axis,self.bbox,self.split_value[self.axis],self.depth,self.points,self.middle_child])  #removed self.parent

        if self.left != None:
            # print(self)
            self.left.itterate_through(boxes,)
            self.right.itterate_through(boxes)
            self.middle.itterate_through(boxes)

        return boxes




    #Print Tree Function
    def print_tree(self,boxes=[],sort=False,whole=False):
        if self.left != None or self.right != None:
            boxes.append([self.axis,self.bbox,self.split_value[self.axis],self.depth,self.points,self.middle_child])
        
        if self.left != None:
            self.left.itterate_through(boxes)
            self.right.itterate_through(boxes)
            self.middle.itterate_through(boxes)
        if sort == True:
            boxes.sort(key=lambda x: x[3])
        print("| Depth\t\t| Split\t\t| Middle\t\t| Range: [xmin, xmax] [ymin, ymax]")
        for item in boxes:
            if item[0] == 1:
                # print(f"| Depth: {item[3]}\t|  Y = {item[2]}\t| Middle: {item[5]}\t| BBOX: {item[1]}")
                print(f"| Depth: {item[3]}\t|  Y = {item[2]}\t| Middle: {item[5]}\t\t| Range: [{item[1][0]}, {item[1][2]}] [{item[1][1]}, {item[1][3]}]\t| Points: {item[4]}")
            else:
                print(f"| Depth: {item[3]}\t|  X = {item[2]}\t| Middle: {item[5]}\t\t| Range: [{item[1][0]}, {item[1][2]}] [{item[1][1]}, {item[1][3]}]\t| Points: {item[4]}")

        if whole == True:
            all_points = self.itterate_through(leaf=True)
            for item in all_points:
                print(f"| Depth: {item[2]}\t| Range: [{item[1][0]}, {item[1][2]}] [{item[1][1]}, {item[1][3]}]\t| Points: {item[3]}")


        
        
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

    

def save_query(tree, xmin=None, ymin=None, xmax=None, ymax=None, num=1, sprout=None, path=None, small=False, medium=False, large=False, save=True, show=False, SRC=False, BRC=False):
    """
    This intakes a KDTree, runs it through a searching method with randomly made bbox values, then saves a csv file to path. If path is not given it will create a .csv file in Saved Query, if no folder exists then it will create it. Currently works for SRC and BRC method, if neither SRC or BRC are stated as true when this method is called it will default to SRC.
    
    :param tree: The KD Tree
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
    i=0
    if xmin==None and ymin==None and xmax==None and ymax==None:     #we need to generate query
        while i < num:      #could change with while num != 0
            if small == True:
                xmin = random.randint(tree.bbox[0],tree.bbox[2])
                xmax = random.randint(xmin-6,xmin+6)
                ymin = random.randint(xmin-6,xmin+6)
                ymax = random.randint(xmin-6,xmin+6)

            elif medium == True:
                xmin = random.randint(tree.bbox[0],tree.bbox[2])
                xmax = random.randint(xmin-20,xmin+20)
                ymin = random.randint(xmin-20,xmin+20)
                ymax = random.randint(xmin-20,xmin+20)

            elif large == True:
                xmin = random.randint(tree.bbox[0],tree.bbox[2])
                xmax = random.randint(xmin-40,xmin+40)
                ymin = random.randint(xmin-40,xmin+40)
                ymax = random.randint(xmin-40,xmin+40)

            else:
                xmin = random.randint(tree.bbox[0],tree.bbox[2])
                xmax = random.randint(tree.bbox[0],tree.bbox[2])
                ymin = random.randint(tree.bbox[1],tree.bbox[3])
                ymax = random.randint(tree.bbox[1],tree.bbox[3])

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
                node = tree.BRC(q_xmin=xmin, q_ymin=ymin, q_xmax=xmax, q_ymax=ymax, result=[])

            if i == 0:          # I feel like if I didn't use pandas, or atleast used it at the end to write to the csv file, this would possibly go faster
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
            i+=1
    else:   #we are given a query range
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
        
        while i < num:      #could technically just use a length of pd.dataframe
            if SRC == True:
                node = tree.SRC(xmin, xmax, ymin, ymax)
            elif BRC == True:
                node = tree.BRC(xmin, ymin, xmax, ymax)
            
            if i == 0:
                if SRC == True:
                    temp = pd.DataFrame([[[xmin,ymin,xmax,ymax],node.depth,node.bbox,node.data_size]], columns=["SRC Query","Depth","BBoxes","Data Size"], index=None)
                elif BRC == True:
                    temp = pd.DataFrame([[[xmin,ymin,xmax,ymax],node,len(node)]], columns=["BRC Query","Points","# Of Points"], index=None)
            else:
                if SRC == True:
                    temp.loc[i] = [xmin,ymin,xmax,ymax],node.depth,node.bbox
                elif BRC == True:
                    temp.loc[i] = [xmin,ymin,xmax,ymax],node,len(node)
            if show == True:
                tree.graph_tree(plot_boxes=[[xmin,ymin,xmax,ymax]])
            i+=1
    if save == True:
        temp.to_csv(path,mode='a',index=None)
    else:
        return print(temp)
    


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



def points_from_file(path=None):        #Need to make it where it can split the csv file with delimeter = ' ' or ','. Also make method to work with .txt
    """
    Reads csv file and returns data in a list (which can straight forward be used in making a KD Tree). Uses Pandas lib.
    
    :param path: Need path (also needs r before path string)
    """
    if path == None:
        return print("Need path!")
    points = pd.read_csv(path)
    points = points.values.tolist()
    return points




#This is entirly to just increase the maximum recursion depth for sorintg
# import sys
# sys.setrecursionlimit(1000) #originally is 1000






# points = make_points(num=10,sprout=8,aRang=0,bRang=5,sort=True)
points = make_points(num=64,sprout=8,aRang=0,bRang=50)
# for item in points:
#     print(item)

# points = make_points(num=22000,sprout=8,aRang=0,bRang=1000)
#100% it has to be the itteration method

temp = KDTree(points)
temp.graph_tree()














#through sys.getsizeof each node hold 48 bytes, the only thing that varies is the leaf nodes (depending on how much data is in them)
# boxes = temp.itterate_through()
# print(len(boxes)*48)
#and it SEEMS that each leaf node holds 16 bytes


### Memory Info ###
#All test points are made in range of 0 to 100000000, and info is from task manager
#1 million points uses 300 MB
#5 million points uses 1150 MB
#10 million points uses 2200 MB

