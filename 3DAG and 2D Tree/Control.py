import Control_helper
import pandas as pd


points = pd.read_csv(r"C:\Users\cvinc\Desktop\College\Internship\Github\Multi-Dimensional-Data-Structure\3DAG and 2D Tree\Saved Datasets\train_integerized.csv")
# points = points[['AB','AH']]
points = list(zip(points['DE'].astype(int),points['AH'].astype(int)))

Control_helper.__main__(num=1000, dataset="Train Integerized", seed=0, points=points)
Control_helper.__main__(num=5000, dataset="Train Integerized", seed=0, points=points)
Control_helper.__main__(num=10000, dataset="Train Integerized", seed=0, points=points)

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






