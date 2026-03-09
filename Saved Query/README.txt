Now, the filing system works like this:
Saved Query
-> 3DAG
	-> CRAWDAD
		-> With Duplicates
			-> Seed - # of queries
		-> Without Duplicates
			-> Seed - # of queries
-> KD
	-> CRAWDAD
		-> With Duplicates
			-> Seed - # of queries
		-> Without Duplicates
			-> Seed - # of queries

In each data folder there will be the csv files, a folder called Report, and a folder called Graphs. In the Report folder there will be 3 csv files that contain the number of points BRC returned (BRC Size), the number of points SRC return (SRC Size), the difference between the two sizes, the False/Positive ratio (F/P %), the depth of the SRC returned node, and the percent error (Error %). You will also find a Summary.txt file which contains the averages of all the data, along with the number of infinite values that we get from the false positive ratio (because SRC Size/BRC Size is an issue, for BRC Size can be 0). To calculate the average false positive ratio I removed the infinite values from the calculation, not the data itself. In the Graphs folder there will just be bar graphs depicting the depth of all returned SRC nodes for large, medium, and small.
