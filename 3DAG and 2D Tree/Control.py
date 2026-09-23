import Control_helper
import pandas as pd

#To get to queries from the Multi-Dimensional-Data-Structure folder is 
    #-> 3DAG and 2D Tree
        #-> Saved Queries
        # Here the dataset (name) of the queries, that you input here, will show up along with a dash, then the number of queries
        #so for example if the dataset="16x16" and num=1000 the folder is:"16x16 - 1000" as 16x16 dataset, 1000 queries
            #-> In a folder from here you will then see DAG and KD folder, which hold information about the told data structure
                #-> In DAG you will see BRC, SRC Exhaustive, SRC Left and Right, SRC Middle, and SRC Random, which hold according information
                    #-> In these folders you will see 3 csv files which hold the algorithims queries and information
                # You will also see the _Graphs and _L2 Norm folders, which both hold according information
                    #-> In the _Graphs folder you will see pngs, being the distribution of thr queries, along with a CSV and Diff folder
                        #-> The Diff folder holds pngs of lvl difference (against KD)
                    #-> In the CSV folder you will see the query level from DAG and KD

#The averages.txt that shows up is the accuracy, SRC/BRC


#for you to start mass queries for 3DAG and KD Trees you must follow these steps:
    # If you have points to input into these trees then you must set them up before, in a list of tuples
    # Call Constrol_helper.__main__()
        # In this function call, you need:
            # num (as an int): this is the number of queries you make
            # dataset (as a string): this is the name of the dataset
            # seed (as an int): queries are randomly made, if you want to seed this randomization add a seed
            # points (not required, list of tuples 2D): points pre made/organized
            # rng (not required), as an int: use this to make a uniform dataset in the range given (if given 16 will only do 0-15)
        # You will need either points or rng


# points = pd.read_csv(r"C:\Users\cvinc\Desktop\College\Internship\Github\Multi-Dimensional-Data-Structure\3DAG and 2D Tree\Saved Datasets\train_integerized.csv")
# points = list(zip(points['DE'].astype(int),points['AH'].astype(int)))

# Control_helper.__main__(num=1000, dataset="Train Integerized", seed=0, points=points)
# Control_helper.__main__(num=5000, dataset="Train Integerized", seed=0, points=points)
# Control_helper.__main__(num=10000, dataset="Train Integerized", seed=0, points=points)

# Control_helper.__main__(num=5, dataset="16x16 With Connectivity", seed=0, rng=16)
# Control_helper.__main__(num=10, dataset="16x16 With Connectivity", seed=0, rng=16)
# Control_helper.__main__(num=100, dataset="16x16 With Connectivity", seed=0, rng=16)

# Control_helper.__main__(num=1000, dataset="16x16 With Connectivity", seed=0, rng=16)
# Control_helper.__main__(num=10000, dataset="16x16 With Connectivity", seed=0, rng=16)
# Control_helper.__main__(num=50000, dataset="16x16 With Connectivity", seed=0, rng=16)

# Control_helper.__main__(num=1000, dataset="32x32 With Connectivity", seed=0, rng=32)
# Control_helper.__main__(num=10000, dataset="32x32 With Connectivity", seed=0, rng=32)
# Control_helper.__main__(num=50000, dataset="32x32 With Connectivity", seed=0, rng=32)

# Control_helper.__main__(num=1000, dataset="64x64 With Connectivity", seed=0, rng=64)
# Control_helper.__main__(num=10000, dataset="64x64 With Connectivity", seed=0, rng=64)
# Control_helper.__main__(num=50000, dataset="64x64 With Connectivity", seed=0, rng=64)

# Control_helper.__main__(num=1000, dataset="128x128 With Connectivity", seed=0, rng=128)
# Control_helper.__main__(num=10000, dataset="128x128 With Connectivity", seed=0, rng=128)
# Control_helper.__main__(num=50000, dataset="128x128 With Connectivity", seed=0, rng=128)






