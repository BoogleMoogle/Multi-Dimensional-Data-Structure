from matplotlib.lines import lineStyles
import matplotlib.pyplot as plt
import random
import pandas as pd
import os

#[xmin x xmax] [ymin x ymax]
class KDTree:
    def __init__(self, points=[], depth=0, axis=0, split_value=None, bbox=[], left=None, right=None, parent=None):   #store data size
        self.left = left
        self.right = right

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
            if item[self.axis] >= self.split_value[self.axis]:      #items with bigger value (right/up)
                right.append(item)  
            else:                                                   #items with lesser value (left/down)
                left.append(item)

        if self.axis == 0:
            self.right = KDTree(right, depth=self.depth+1, axis=1, bbox=[self.split_value[self.axis], self.bbox[1], self.bbox[2], self.bbox[3]], parent=self)
            self.left = KDTree(left, depth=self.depth+1, axis=1, bbox=[self.bbox[0], self.bbox[1], self.split_value[self.axis], self.bbox[3]], parent=self)
        else:
            self.right = KDTree(right, depth=self.depth+1, axis=0, bbox=[self.bbox[0], self.split_value[self.axis], self.bbox[2], self.bbox[3]], parent=self)
            self.left = KDTree(left,  depth=self.depth+1, axis=0, bbox=[self.bbox[0], self.bbox[1], self.bbox[2], self.split_value[self.axis]], parent=self)
 

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
            # if self.left.bbox[0] <= q_xmin and self.left.bbox[2] > q_xmax and self.left.bbox[1] <= q_ymin and self.left.bbox[3] > q_ymax and self.right.bbox[0] <= q_xmin and self.right.bbox[2] >= q_xmax and self.right.bbox[1] <= q_ymin and self.right.bbox[3] >= q_ymax:
            #     return self
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



    #Graph Tree Function
    def graph_tree(self,plot_boxes=None):
        x = []
        y = []
        for item in self.points:
            x.append(item[0])
            y.append(item[1])
        plt.scatter(x, y, c='grey', marker='o')
 
        plt.vlines(x=self.bbox[2],ymin=self.bbox[1],ymax=self.bbox[3],linestyles=':')
        plt.vlines(x=self.bbox[0],ymin=self.bbox[1],ymax=self.bbox[3],linestyles=':')
        plt.hlines(y=self.bbox[3],xmin=self.bbox[0],xmax=self.bbox[2],color='red',linestyles=':')
        plt.hlines(y=self.bbox[1],xmin=self.bbox[0],xmax=self.bbox[2],color='red',linestyles=':')

        boxes = self.itterate_through()
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



    #Itteratting Through KDTree Function
    def itterate_through(self,boxes=[]):
        '''
        Returns [self.axis, self.bbox, self.split_value[self.axis], and self.depth, self.parent, self.points] in that order
        
        :param self: Description
        :param boxes: Description
        :param all: Description
        '''
        if self.split_value != None:
            boxes.append([self.axis,self.bbox,self.split_value[self.axis],self.depth,self.parent,self.points])
        if self.left != None:
            # print(self)
            self.left.itterate_through(boxes)
            self.right.itterate_through(boxes)
        return boxes



    #Print Tree Function        -- Want me to add the range of each node (range - x,y min and max values)
    def print_tree(self,sort=False):
        temp = []
        data = self.itterate_through()
        for item in data:
            if item[0] == 0:    #x axis
                temp.append([item[3],item[2],0,item[1]])
            else:               #y axis
                temp.append([item[3],item[2],1,item[1]])
        if sort == True:
            temp.sort()
        print("| Depth\t\t| Split Node:\t\t| Range: [xmin, xmax] [ymin, ymax]")
        for item in temp:
            if item[2] == 0:
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
            node = tree.SRC(xmin, xmax, ymin, ymax)
            # axis = node.axis

            if i == 0:          # I feel like if I didn't use pandas, or atleast used it at the end to write to the csv file, this would possibly go faster
                if small == True:
                    temp = pd.DataFrame([[[xmin,ymin,xmax,ymax],node.depth,node.bbox]], columns=["Query: Small","Depth","BBoxes"], index=None)
                elif medium == True:
                    temp = pd.DataFrame([[[xmin,ymin,xmax,ymax],node.depth,node.bbox]], columns=["Query: Medium","Depth","BBoxes"], index=None)
                elif large == True:
                    temp = pd.DataFrame([[[xmin,ymin,xmax,ymax],node.depth,node.bbox]], columns=["Query: Large","Depth","BBoxes"], index=None)
                else:
                    temp = pd.DataFrame([[[xmin,ymin,xmax,ymax],node.depth,node.bbox]], columns=["Query","Depth","BBoxes"], index=None)

            else:
                temp.loc[i] = [xmin,ymin,xmax,ymax],node.depth,node.bbox
            if show == True:
                tree.graph_tree(plot_boxes=[[xmin,ymin,xmax,ymax]])
            i+=1
    else:
        while i < num:
            node = tree.SRC(xmin, xmax, ymin, ymax)
            if i == 0:
                temp = pd.DataFrame([[[xmin,ymin,xmax,ymax],node.depth,node.bbox]], columns=["Query","Depth","BBoxes"], index=None)
            else:
                temp.loc[i] = [xmin,ymin,xmax,ymax],node.depth,node.bbox
            if show == True:
                tree.graph_tree(plot_boxes=[[xmin,ymin,xmax,ymax]])
            i+=1
    if save == True:
        temp.to_csv(path,mode='a',index=None)
    else:
        return print(temp)
    



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




### First Data Set (10 Points) ###
# points = [(2,3),(4,1),(6,8),(7,2),(9,6),(8,8),(3,7),(5,4),(7,9),(1,9)]
# temp = KDTree(points)



### Second Data Set (50 Points) ###
# points = [(2,3),(4,1),(6,8),(7,2),(9,6),(8,8),(3,7),(5,4),(7,9),(1,9),(12,15),(18,22),(25,30),(33,27),(40,10),(45,55),(52,48),(60,12),(68,75),(70,40),(5,90),(14,65),(20,80),(28,50),(35,95),(42,70),(50,5),(58,33),(63,88),(72,60),(80,20),(85,45),(90,10),(95,35),(100,100),(0,0),(10,50),(22,11),(37,62),(49,29),(55,90),(61,14),(66,58),(73,97),(78,66),(82,3),(88,77),(91,52),(97,18),(100,0)]



### Making Points ###
points = make_points(num=50,sprout=5,aRang=0,bRang=100)
# print(points)
temp = KDTree(points)

temp.graph_tree()

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