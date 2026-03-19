from re import split
import matplotlib.pyplot as plt

class KDTree:
    def __init__(self, points=[], depth=0, max_depth=0, axis=0, split_value=None, bbox=[], left=None, right=None, parent=None):
        self.left = left
        self.right = right

        self.parent = parent

        if axis == 0:   #sort by x values
            points.sort()
            self.points=points
        else:           #sort by y values
            points.sort(key=lambda x: x[1])
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
                return f"Split Node: x = {self.split_value[self.axis]}, Level: {self.depth}, Left: {self.left}, Right: {self.right}"
            else:
                return f"y = {self.split_value[self.axis]}"
        else:
            return f"Points: {self.points}"
    
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
            self.left = KDTree(left, depth=self.depth+1, axis=0, bbox=[self.bbox[0], self.bbox[1], self.bbox[2], self.split_value[self.axis]], parent=self)




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
        

    
    def nSRC(self, xmin, ymin, xmax, ymax):
        if self.split_value == None:
            return self
        if self.bbox[0] <= xmin and self.bbox[2] >= xmax and self.bbox[1] <= ymin and self.bbox[3] >= ymax: #this node 100% contains the range
            if self.left.bbox[0] <= xmin and self.left.bbox[2] > xmax and self.left.bbox[1] <= ymin and self.left.bbox[3] > ymax and self.right.bbox[0] <= xmin and self.right.bbox[2] >= xmax and self.right.bbox[1] <= ymin and self.right.bbox[3] >= ymax:
                return self
            elif self.axis == 1:
                if self.left.bbox[2] >= xmax and self.left.bbox[3] > ymax:
                    return self.left.nSRC(xmin, ymin, xmax, ymax)
                elif self.right.bbox[0] <= xmin and self.right.bbox[1] <= ymin:
                    return self.right.nSRC(xmin, ymin, xmax, ymax)
            else:
                if self.left.bbox[2] > xmax and self.left.bbox[3] >= ymax:
                    return self.left.nSRC(xmin, ymin, xmax, ymax)
                elif self.right.bbox[0] <= xmin and self.right.bbox[1] <= ymin:
                    return self.right.nSRC(xmin, ymin, xmax, ymax)
        else:
            return self
        return self

           
        

    # def print_tree(self, depth=0):
    #     if self.depth == depth:
    #         print(f"{self.depth}:\t{self}")

    #     if self.split_value != None:
    #         self.left.print_tree()
    #         self.right.print_tree()
    #     else:
    #         self.print_tree(self.depth+1)




     # pTmp = self
        # while pTmp.left!=None:
        #     max_depth+=1
        #     pTmp=pTmp.left
        # pTmp = self
        # level = [(f"{pTmp.depth}",pTmp)]
        # for i in range(max_depth):
        #     while pTmp.right != None:
        #         while pTmp.left != None:
        #             level.append([(f"{pTmp.depth}",f"{pTmp}")])
        #             # print("left")
        #             pTmp = pTmp.left
        #         pTmp=pTmp.parent
        #         # print("right")
        #         level.append([(f"{pTmp.depth}",f"{pTmp.left}")])
        #         pTmp = pTmp.right
        #         level.append(pTmp)
        #         i+=1 
        #     pTmp=self.right

        # for item in level:
        #     print(item)





        
    def graph_tree(self):
        data = self.points
        x = []
        y = []
        for item in self.points:
            x.append(item[0])
            y.append(item[1])
        plt.scatter(x, y, c='black', marker='o')
        splits=[]
        flag = True
        temp = len(data)
        i = 0

        while flag:         #gets how many times a split would have to be done
            if temp > 4:
                temp = temp/2
                i+=1
            else:
                flag = False
        

        # right_f = True
        # left_f = True
        # pTmp = self
        # while flag:
        #     while right_f:
        #         splits.append([pTmp.axis, pTmp.split_value[pTmp.axis]])
        #         # print(pTmp.split_value)
        #         if pTmp.right.split_value != None:
        #             pTmp = pTmp.right
        #         else:
        #             right_f = False
        #     pTmp = pTmp.parent.left
        #     print(pTmp)
        #     flag = False
        # print(splits)
        # plt.show()



       

        
        



        
        
        




points = [(2,3),(4,1),(6,8),(7,2),(9,6),(8,8),(3,7),(5,4),(7,9),(1,9)]

temp = KDTree(points)

# print(temp.SRC(7,8,9,9))
# print(temp.nSRC(1,3,5,3))
# temp.print_tree()
# print(temp.left.left.bbox)

temp.graph_tree()



# print(f"{temp.depth}:\t{temp}\t{temp.bbox}")
# print(f"{temp.left.depth}:\t{temp.left}\t{temp.left.bbox}\t{temp.right}\t{temp.right.bbox}")
# print(f"{temp.left.left.depth}:\t{temp.left.left}\t{temp.left.left.bbox}\t{temp.left.right}\t{temp.left.right.bbox}\t{temp.right.left}\t{temp.right.left.bbox}\t{temp.right.right}\t{temp.right.right.bbox}")
# print(f"\n{temp.bbox}")


#Generate Queries for SRC, make print tree method (level, bbox, split, children/parent)


#Double check it's working, regenerate 50 points, use seed. Make each point a leaf node
# points = [(2,3),(4,1),(6,8),(7,2),(9,6),(8,8),(3,7),(5,4),(7,9),(1,9),(12,15),(18,22),(25,30),(33,27),(40,10),(45,55),(52,48),(60,12),(68,75),(70,40),(5,90),(14,65),(20,80),(28,50),(35,95),(42,70),(50,5),(58,33),(63,88),(72,60),(80,20),(85,45),(90,10),(95,35),(100,100),(0,0),(10,50),(22,11),(37,62),(49,29),(55,90),(61,14),(66,58),(73,97),(78,66),(82,3),(88,77),(91,52),(97,18),(100,0)]


# temp = KDTree(points)
# temp.print_tree()