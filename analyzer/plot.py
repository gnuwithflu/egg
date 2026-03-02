import numpy as np
import matplotlib.pyplot as plt
import ast
import numpy as np

f = open("analyzer/dataset_cici.txt", "r")

data = ast.literal_eval(f.read())

plt.figure(figsize=(7, 6))

im = plt.imshow(data, cmap="viridis", origin="lower", aspect="auto")
plt.colorbar(im, label="Time in h")

plt.title("CICI wait times")
plt.xlabel("Curiosity time [h]")
plt.ylabel("Integrity time [h]")


nrows = 100
ncols = 100

# X axis
x_ticks = np.arange(ncols)
plt.xticks(x_ticks, np.round(x_ticks / 2.5/100,2))

# Y axis
y_ticks = np.arange(nrows)
plt.yticks(y_ticks, np.round(y_ticks / 2.5/100,2))


plt.tight_layout()
plt.savefig("CICI wait times 5te fine.png")
plt.show()