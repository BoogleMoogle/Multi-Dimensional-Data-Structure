from matplotlib.lines import lineStyles
import matplotlib.pyplot as plt
import random
import pandas as pd
import os

class KDTree:
    def __init__(self, points=[], depth=0, splits=[], axis=0, split_value=None, bbox=[], left=None, right=None, parent=None):
        self.left = left
        self.right = right

        self.parent = parent
        self.splits = splits
        if axis == 0:   #sort by x values
            points.sort()
            self.points=points
        else:           #sort by y values
            points.sort(key=lambda x: x[1])     #!!!If range is too short then it will crash
            self.points=points

        self.depth=depth
        self.axis=axis
        self.split_value=split_value

        if len(bbox) == 0:      #only need to find bbox for first time
            self.bbox = self.find_bbox(bbox)
        else:
            self.bbox = bbox

        if len(self.points) > 4:
            self.split(self.splits)


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
    def split(self,splits=None):
        # print("Split!!!")

        self.split_value = self.points[len(self.points)//2]
        splits.append([self.axis,self.split_value[self.axis]])
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
        self.splits = splits



    #Single Range Cover Method
    def SRC(self,xmin,ymin,xmax,ymax):
        if self.split_value == None:
            return self
        if self.bbox[0] == xmin and self.bbox[1] == ymin and self.bbox[2] == xmax and self.bbox[3] == ymax:
            return self
        
        if self.axis == 0:      #deal with xs
            if xmax >= self.split_value[0]:     #would need to go right
                if xmin >= self.right.bbox[0]:
                    # if self.right.split_value != None:
                    return self.right.SRC(xmin,ymin,xmax,ymax)
                    # else:
                    #     return self
                else:
                    if self.left.bbox[0] > xmin and self.right.bbox[0] <= xmax:
                        return self
                    elif self.left.bbox[2] > xmax:
                        return self.left
                    else:
                        return self.right
                        
                    
            if xmin < self.split_value[0]:      #would need to go left
                if xmax < self.left.bbox[2]:
                    # if self.left.split_value != None:
                    return self.left.SRC(xmin,ymin,xmax,ymax)
                    # else:
                    #     return self
                else:
                    if self.left.bbox[0] >= xmin and self.right.bbox[0] <= xmax:     #>= ymin
                        return self
                    elif self.left.bbox[2] > xmax:
                        return self.left
                    else:
                        return self.right
                
        elif self.axis == 1:    #deal with ys
            if ymax > self.split_value[1]:
                if ymin > self.right.bbox[1]:
                    # if self.right.split_value != None:
                    return self.right.SRC(xmin,ymin,xmax,ymax)
                    # else:
                        # return self
                else:
                    if self.left.bbox[3] > ymin and self.right.bbox[1] <= ymax:
                        return self
                    elif self.left.bbox[3] > ymax:
                        return self.left
                    else:
                        return self.right
                    
            if ymin <= self.split_value[1]:
                if ymax > self.left.bbox[3]:
                    return self.right.SRC(xmin,ymin,xmax,ymax)

                else:   #need to now check values of left and right leaf nodes
                    if self.left.bbox[1] >= ymin and self.right.bbox[1] <= ymax:     #>= ymin
                        return self
                    elif self.left.bbox[3] > ymax:
                        return self.left
                    else:
                        return self.right
        else:
            return self
        

    
    def SRC(self, xmin, ymin, xmax, ymax):
        if xmin > xmax:
            temp = xmax
            xmax = xmin
            xmin = temp
        if ymin > ymax:
            temp = ymax
            ymax = ymin
            ymin = temp
            
        if self.split_value == None:
            return self
        if self.bbox[0] <= xmin and self.bbox[2] >= xmax and self.bbox[1] <= ymin and self.bbox[3] >= ymax: #this node 100% contains the range
            if self.left.bbox[0] <= xmin and self.left.bbox[2] > xmax and self.left.bbox[1] <= ymin and self.left.bbox[3] > ymax and self.right.bbox[0] <= xmin and self.right.bbox[2] >= xmax and self.right.bbox[1] <= ymin and self.right.bbox[3] >= ymax:
                return self
            elif self.axis == 1:
                if self.left.bbox[2] >= xmax and self.left.bbox[3] > ymax:
                    return self.left.SRC(xmin, ymin, xmax, ymax)
                elif self.right.bbox[0] <= xmin and self.right.bbox[1] <= ymin:
                    return self.right.SRC(xmin, ymin, xmax, ymax)
            else:
                if self.left.bbox[2] > xmax and self.left.bbox[3] >= ymax:
                    return self.left.SRC(xmin, ymin, xmax, ymax)
                elif self.right.bbox[0] <= xmin and self.right.bbox[1] <= ymin:
                    return self.right.SRC(xmin, ymin, xmax, ymax)
        else:
            return self
        return self

        
    def graph_tree(self):
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

        plt.tight_layout()
        plt.show()


    def itterate_through(self,boxes=[], all=False):
        if self.split_value != None:
            if all == True:
                boxes.append([self.points,self.axis,self.bbox,self.split_value[self.axis],self.depth])
            else:
                boxes.append([self.axis,self.bbox,self.split_value[self.axis],self.depth])
        if self.left != None:
            # print(self)
            self.left.itterate_through(boxes,all)
            self.right.itterate_through(boxes,all)
        return boxes



    def print_tree(self,sorted=False):
        temp = []
        data = self.itterate_through()
        for item in data:
            if item[0] == 0:    #x axis
                temp.append([item[3],item[2],0])
            else:               #y axis
                temp.append([item[3],item[2],1])
        #item[3] is depth and item[2] is split value
        if sorted == True:
            temp.sort()
        for item in temp:
            if item[2] == 0:
                print(f"Depth: {item[0]}\tX = {item[1]}")
            else:
                print(f"Depth: {item[0]}\tY = {item[1]}")


        
        
###### General Use Methods ######
def make_points(num=1, sprout=None, aRang=0, bRang=100):
    temp = []
    if sprout != None:
        random.seed(sprout)
    while len(temp) < num:
        temp.append((random.randint(aRang,bRang),random.randint(aRang,bRang)))
    return temp

    

def save_query(tree, xmin=None,ymin=None,xmax=None,ymax=None, num=1, sprout=None, path=None, small=False, medium=False, large=False):
    if sprout != None:
        random.seed(sprout)
    if path == None:
        return print("Need path!")
    i=0
    if xmin==None and ymin==None and xmax==None and ymax==None:     #we need to generate query
        while i < num:
            if small == True:
                xmin = random.randint(tree.bbox[0],tree.bbox[2])
                xmax = random.randint(xmin-6,xmin+6)
                ymin = random.randint(tree.bbox[1],tree.bbox[3])
                ymax = random.randint(ymin-6,ymin+6)

            elif medium == True:
                xmin = random.randint(tree.bbox[0],tree.bbox[2])
                xmax = random.randint(xmin-20,xmin+20)
                ymin = random.randint(tree.bbox[1],tree.bbox[3])
                ymax = random.randint(ymin-20,ymin+20)

            elif large == True:
                xmin = random.randint(tree.bbox[0],tree.bbox[2])
                xmax = random.randint(xmin-40,xmin+40)
                ymin = random.randint(tree.bbox[1],tree.bbox[3])
                ymax = random.randint(ymin-40,ymin+40)

            else:
                xmin = random.randint(tree.bbox[0],tree.bbox[2])
                xmax = random.randint(tree.bbox[0],tree.bbox[2])
                ymin = random.randint(tree.bbox[1],tree.bbox[3])
                ymax = random.randint(tree.bbox[1],tree.bbox[3])

            node = tree.SRC(xmin, xmax, ymin, ymax)
            if i == 0:
                if small == True:
                    temp = pd.DataFrame([[[xmin,ymin,xmax,ymax],node.depth,node.bbox]], columns=["Query: Small","Depth","Bboxes"], index=None)
                elif medium == True:
                    temp = pd.DataFrame([[[xmin,ymin,xmax,ymax],node.depth,node.bbox]], columns=["Query: Medium","Depth","Bboxes"], index=None)
                elif large == True:
                    temp = pd.DataFrame([[[xmin,ymin,xmax,ymax],node.depth,node.bbox]], columns=["Query: Large","Depth","Bboxes"], index=None)
                else:
                    temp = pd.DataFrame([[[xmin,ymin,xmax,ymax],node.depth,node.bbox]], columns=["Query","Depth","Bboxes"], index=None)

            else:
                temp.loc[i] = [xmin,ymin,xmax,ymax],node.depth,node.bbox
            i+=1
    else:
        while i < num:
            node = tree.SRC(xmin, xmax, ymin, ymax)
            if i == 0:
                temp = pd.DataFrame([[[xmin,ymin,xmax,ymax],node.depth,node.bbox]], columns=["Query","Depth","Bboxes"], index=None)
            else:
                temp.loc[i] = [xmin,ymin,xmax,ymax],node.depth,node.bbox
            i+=1
    temp.to_csv(path,mode='a',index=None)



def save_tree(tree,path=None):
    if path == None:
        path = f"Saved KD Trees/temp {len(os.listdir('Saved KD Trees'))+1}.csv"

    df = pd.DataFrame((tree.points),index=None)
    df.to_csv(path,index=False,header=False)



def points_from_file(path=None):
    if path == None:
        return print("Need path!")
    temp = []
    points = pd.read_csv(path)
    points = points.values.tolist()
    return points




# points = [(2,3),(4,1),(6,8),(7,2),(9,6),(8,8),(3,7),(5,4),(7,9),(1,9)]
# print(f"{points}\n")
# temp = KDTree(points)
# bboxes = temp.itterate_through()
# print(bboxes)
# temp.graph_tree()

# print(temp.splits)

# print(temp.SRC(7,8,9,9))
# print(temp.nSRC(1,3,5,3))
# temp.print_tree()




# print(f"{temp.depth}:\t{temp}\t{temp.bbox}")
# print(f"{temp.left.depth}:\t{temp.left}\t{temp.left.bbox}\t{temp.right}\t{temp.right.bbox}")
# print(f"{temp.left.left.depth}:\t{temp.left.left}\t{temp.left.left.bbox}\t{temp.left.right}\t{temp.left.right.bbox}\t{temp.right.left}\t{temp.right.left.bbox}\t{temp.right.right}\t{temp.right.right.bbox}")
# print(f"\n{temp.bbox}")


#Generate Queries for SRC, make print tree method (level, bbox, split, children/parent)


#Double check it's working, regenerate 50 points, use seed. Make each point a leaf node
# points = [(2,3),(4,1),(6,8),(7,2),(9,6),(8,8),(3,7),(5,4),(7,9),(1,9),(12,15),(18,22),(25,30),(33,27),(40,10),(45,55),(52,48),(60,12),(68,75),(70,40),(5,90),(14,65),(20,80),(28,50),(35,95),(42,70),(50,5),(58,33),(63,88),(72,60),(80,20),(85,45),(90,10),(95,35),(100,100),(0,0),(10,50),(22,11),(37,62),(49,29),(55,90),(61,14),(66,58),(73,97),(78,66),(82,3),(88,77),(91,52),(97,18),(100,0)]
# print(len(points))

# temp = KDTree(points)

# print(temp.nSRC(8,20,70,30))

# temp.print_tree()

# bboxes = temp.itterate_through()

# print(len(bboxes))
# for item in bboxes:
#     # if item[0] == 1:
#     print(item)


# print(temp.left.left.left.left.axis)

# temp.graph_tree()
# print(temp)







points = make_points(50,sprout=6,aRang=0,bRang=100)
# print(points)
temp = KDTree(points)
# print(temp.splits)
# temp.graph_tree()
# temp.print_tree()
# iterations = temp.itterate_through(all=True)
# print(iterations)
# path = r"C:\Users\cvinc\Desktop\College\Internship\WarmUp\Saved KD Trees\temp 3.csv"
# save_tree(temp)
# points = points_from_file(path)
# temp = KDTree(points)
# temp.graph_tree()


# path = r'C:\Users\cvinc\Desktop\College\Internship\WarmUp\Saved Query\temp.csv'
# save_query(temp,num=10,path=path,small=True)
# save_query(temp,num=10,path=path,medium=True)
# save_query(temp,num=10,path=path,large=True)
