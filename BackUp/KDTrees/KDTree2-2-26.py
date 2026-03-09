from matplotlib.lines import lineStyles
import matplotlib.pyplot as plt
import random
import pandas as pd
import os
from math import ceil

from shapely import point_on_surface


class KDTree:
    def __init__(self, points=[], depth=0, axis=0, split_value=None, bbox=[], left=None, right=None, parent=None):   #store data size
        self.left = left
        self.right = right

        self.data_size = len(points)
        self.parent = parent
        if axis == 0:   #sort by x values
            points.sort()
            self.points=points
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

        if len(self.points) > 4:
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
        self.split_value = self.points[len(self.points)//2]
        #find points that go left (down) and right (up)
        right = []
        left=[]
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

        # print(f"Len of Right: {len(right)}")
        # print(f"Len of Left: {len(left)}")
        # print(f"Half of Self Length: {len(self.points)//2}")
        # print(f"Self Split Value: {self.split_value}\n")

        if self.axis == 0:
            self.left = KDTree(left, depth=self.depth+1, axis=1, bbox=[self.bbox[0], self.bbox[1], self.split_value[self.axis], self.bbox[3]], parent=self)
            self.right = KDTree(right, depth=self.depth+1, axis=1, bbox=[self.split_value[self.axis], self.bbox[1], self.bbox[2], self.bbox[3]], parent=self)

        else:
            self.left = KDTree(left,  depth=self.depth+1, axis=0, bbox=[self.bbox[0], self.bbox[1], self.bbox[2], self.split_value[self.axis]], parent=self)
            self.right = KDTree(right, depth=self.depth+1, axis=0, bbox=[self.bbox[0], self.split_value[self.axis], self.bbox[2], self.bbox[3]], parent=self)
        self.points = None



    #Single Range Cover Search Method
    def SRC(self, q_xmin, q_ymin, q_xmax, q_ymax, graph=False):
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
                if self.left.bbox[2] >= q_xmax and self.left.bbox[3] > q_ymax:      #self.bbox[q_xmin,q_ymin,q_xmax,q_ymax]
                    return self.left.SRC(q_xmin, q_ymin, q_xmax, q_ymax)
                elif self.right.bbox[0] <= q_xmin and self.right.bbox[1] <= q_ymin:
                    return self.right.SRC(q_xmin, q_ymin, q_xmax, q_ymax)
            else:
                if self.left.bbox[2] > q_xmax and self.left.bbox[3] >= q_ymax:
                    return self.left.SRC(q_xmin, q_ymin, q_xmax, q_ymax)
                elif self.right.bbox[0] <= q_xmin and self.right.bbox[1] <= q_ymin:
                    return self.right.SRC(q_xmin, q_ymin, q_xmax, q_ymax)
        else:
            return self
        return self



    #BRC Searching Method
    def BRC(self, q_xmin, q_ymin, q_xmax, q_ymax, result=[]):
        if self.points != None:
            for item in self.points:
                print(item)
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

    #Graph Tree Function
    def graph_tree(self,plot_boxes=None):
        x = []
        y = []
        boxes = self.itterate_through(leaf=True)

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
                plt.vlines(x=item[2],ymin=item[1][1],ymax=item[1][3],linestyles=':')        #x is 

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




    #Itteratting Through KDTree Function
    def itterate_through(self,boxes=[],leaf=False,leaf_nodes=[]):
        '''
        Returns [self.axis, self.bbox, self.split_value[self.axis], and self.depth, self.points] in that order
        
        :param self: Description
        :param boxes: Description
        :param leaf: If True will return only the leaf nodes of KDTree
        '''
        if leaf == False or leaf == None:
            if self.split_value != None:
                boxes.append([self.axis,self.bbox,self.split_value[self.axis],self.depth,self.points])  #removed self.parent
        
        if self.left != None:
            # print(self)
            self.left.itterate_through(boxes,leaf)
            self.right.itterate_through(boxes,leaf)
        elif leaf == True or all ==True:
            leaf_nodes.append([self.axis,self.bbox,self.depth,self.points])

        if all == True:
            print(boxes + leaf_nodes)
        if leaf == False:
            return boxes
        else:
            return leaf_nodes



    #Print Tree Function        -- Want me to add the range of each node (range - x,y min and max values)
    def print_tree(self,sort=False,whole=False):
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

    

def save_query(tree, xmin=None,ymin=None,xmax=None,ymax=None, num=1, sprout=None, path=None, small=False, medium=False, large=False, save=True, show=False):
    """
    This intakes a KDTree, runs it through a SRC method with randomly made bbox values, then saves a csv file to path. If path is not given it will create a .csv file in Saved Query, if no folder exists then it will create it.
    
    :param tree: The KD Tree
    :param xmin: x minimum of SRC search
    :param ymin: y minimum of SRC search
    :param xmax: x maximum of SRC search
    :param ymax: y maximum of SRC search
    :param num: The amount of queries repeated
    :param sprout: Seed for random xmin, ymin, xmax, and y max
    :param path: Optional, need r before path string
    :param small: Generates random xmin and y min, then xmax and ymax are 6 points either above or below it (sorted later)
    :param medium: Generates random xmin and y min, then xmax and ymax are 20 points either above or below it (sorted later)
    :param large: Generates random xmin and y min, then xmax and ymax are 40 points either above or below it (sorted later)
    :param save: If False, will not save to file
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
        while i < num:
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

            if xmin > xmax:
                a = xmax
                xmax = xmin
                xmin = a
            if ymin > ymax:
                a = ymax
                ymax = ymin
                ymin = a

            if xmin < tree.bbox[0]:
                xmin = tree.bbox[0]
            if xmax > tree.bbox[2]:
                xmax = tree.bbox[2]
            if ymin < tree.bbox[1]:
                ymin = tree.bbox[1]
            if ymax > tree.bbox[3]:
                ymax = tree.bbox[3]
            node = tree.SRC(xmin, xmax, ymin, ymax)
            # axis = node.axis

            if i == 0:          # I feel like if I didn't use pandas, or atleast used it at the end to write to the csv file, this would possibly go faster
                if small == True:
                    temp = pd.DataFrame([[[xmin,ymin,xmax,ymax],node.depth,node.bbox,node.data_size]], columns=["Query: Small","Depth","BBoxes","Data Size"], index=None)
                elif medium == True:
                    temp = pd.DataFrame([[[xmin,ymin,xmax,ymax],node.depth,node.bbox,node.data_size]], columns=["Query: Medium","Depth","BBoxes","Data Size"], index=None)
                elif large == True:
                    temp = pd.DataFrame([[[xmin,ymin,xmax,ymax],node.depth,node.bbox,node.data_size]], columns=["Query: Large","Depth","BBoxes","Data Size"], index=None)
                else:
                    temp = pd.DataFrame([[[xmin,ymin,xmax,ymax],node.depth,node.bbox,node.data_size]], columns=["Query","Depth","BBoxes","Data Size"], index=None)

            else:
                temp.loc[i] = [xmin,ymin,xmax,ymax],node.depth,node.bbox,node.data_size
            if show == True:
                tree.graph_tree(plot_boxes=[[xmin,ymin,xmax,ymax]])
            i+=1
    else:
        while i < num:
            node = tree.SRC(xmin, xmax, ymin, ymax)
            if i == 0:
                temp = pd.DataFrame([[[xmin,ymin,xmax,ymax],node.depth,node.bbox,node.data_size]], columns=["Query","Depth","BBoxes","Data Size"], index=None)
            else:
                temp.loc[i] = [xmin,ymin,xmax,ymax],node.depth,node.bbox
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






# points = make_points(num=50,sprout=5,aRang=0,bRang=100)
# points = make_points(num=64,sprout=8,aRang=0,bRang=50)

# temp = KDTree(points)
# temp.print_tree()
# save_query(temp,num=50,large=True,sprout=6,save=False,show=True)         #Q: 68, 74, 73, 79
# temp.graph_tree()

# path=r"C:\Users\cvinc\Desktop\College\Internship\WarmUp\Saved KD Trees\Tests\House Data-Price and SqrFt.csv"
# points=points_from_file(path=path)

# points = make_points(num=64,sprout=2,aRang=0,bRang=50)

# temp = KDTree(points)
# temp.print_tree()
# temp.graph_tree()

points = make_points(num=20,sprout=2,aRang=0,bRang=30)
# points=[]
# for i in range(8):
#     for j in range(8):
#         points.append((i,j))

# for item in points:
#     print(item)

temp = KDTree(points)
temp.print_tree(whole=True,sort=True)
# temp.graph_tree()
# nodes = temp.get_all_nodes()
# for item in nodes:
#     print(item)
# print(temp.left.left.left)





# path=r"C:\Users\cvinc\Desktop\College\Internship\WarmUp\Saved Query\2-2-26.csv"
# save_query(temp,num=20,small=True,sprout=6,path=path,save=True,show=False)
# save_query(temp,num=20,medium=True,sprout=6,path=path,save=True,show=False)
# save_query(temp,num=20,large=True,sprout=6,path=path,save=True,show=False)
# print(temp.BRC(20,20,40,25))



########    General Test    ########

### Making Points ###
# points = make_points(num=50,sprout=5,aRang=0,bRang=100)
# print(points)

# temp = KDTree(points)
# temp.print_tree()

### Points From .csv ###
# path = r"C:\Users\cvinc\Desktop\College\Internship\WarmUp\Saved KD Trees\Tests\archive\2d_data.csv"
# points = points_from_file(path)
# temp = KDTree(points)



### Graphing Function ###
# temp.graph_tree()



### Saving Query ###
# save_query(temp,num=1,small=True,sprout=6,save=False,show=True)         #Q: 68, 74, 73, 79




# path=r"C:\Users\cvinc\Desktop\College\Internship\WarmUp\Saved Query\Show This One.csv"
# save_query(temp,num=10,small=True,save=True,show=False)
# save_query(temp,num=10,medium=True,save=True,show=False)
# save_query(temp,num=10,large=True,save=True,show=False)




# plot_boxes = [[0.05,0.1,0.15,0.2],
#               [0.1,0.15,0.3,0.4]]
# plot_boxes = [[46, 43, 83, 79],[83, 53, 100, 97],[0, 0, 20, 32]]
# plot_boxes =[[8, -28, 13, 43]]
# temp.graph_tree(plot_boxes)



# print(temp.left.left.left.points)