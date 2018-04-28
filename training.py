import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.utils import shuffle
from sklearn.preprocessing import scale

'''
Format of input datafile
No F1 F2 F3 F4 F5 T
F = [ [F1, F2, F3, F4, F5],
      [F1, F2, F3, F4, F5],
             ......
      [F1, F2, F3, F4, F5] ]
T = [T, T, ...... T]
'''

# load training data
T = []
F = []

# setting
N_DATA = 1000
T_DATA = tf.float64


# get the training data ready
F, T = shuffle(F, T)
X = scale(F[:N_DATA])
Y = T[:N_DATA]

nF = len(F[0])

# calculate error
W = tf.Variable(tf.random_normal([nF,1], name='weight', mean=1, stddev=0.0, dtype=T_DATA))
f = tf.placeholder(T_DATA)
t = tf.placeholder(T_DATA)
b = tf.Variable(tf.zeros(1, dtype=T_DATA))
E = tf.add(b, tf.matmul(f, W))
squared_deltas = tf.square(t - E)
error = tf.reduce_mean(squared_deltas)

# get training session ready
init = tf.global_variables_initializer()
optimizer = tf.train.GradientDescentOptimizer(0.01).minimize(error)
cost_history = []
weight_history = [[] for i in range(nF)]

with tf.Session() as sess:
    sess.run(init)
    print('init w', sess.run(W, {f: F, t: T}))

    for i in range(N_DATA):
        sess.run(optimizer, {f: F, t: T})

        # Record wight
        if i % 10 == 0:
            for j in range(nF):
                weight_history[j].append(sess.run(W, {f: F, t: T})[j])
        # Display error
        if i % 500 == 0:
            print('error', sess.run(error, {f: F, t: T}))

    # Plot weight history
    for i in range(len(weight_history)):
        plt.plot(weight_history[i])
    print('final w', sess.run(W, {f: F, t: T}))
    plt.show()
    sess.close()