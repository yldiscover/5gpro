# -*- coding: utf-8 -*-

import os
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.python.framework import ops
ops.reset_default_graph()


# Genetic Algorithm Parameters
pop_size = 100
features = 50
selection = 0.2
mutation = 1./pop_size
generations = 200
num_parents = int(pop_size*selection)
num_children = pop_size - num_parents

# Start a graph session
sess = tf.Session()

# Create ground truth
#truth = np.sin(2*np.pi*(np.arange(features, dtype=np.float32))/features)
truth = np.array([0.1,0.2,0.3,0.14,0.25,0.6,0.7,0.18,0.9,0,0.21,0.22,0.33,0.4,0.5,0.16,0.27,0.8,0.9,0.1,0.1,0.22,0.33,0.34,0.5,0.96,0.7,0.8,0.29,0.002,0.21,0.32,0.3,0.34,0.65,0.6,0.7,0.8,0.9,0.0,0.31,0.52,0.3,0.4,0.55,0.6,0.67,0.8,0.29,0.8,])
print "===================",len(truth)
print truth
print "###################"

#truth = np.sin(2*np.pi*(np.arange(features, dtype=np.float32))/features)

# Initialize population array
population = tf.Variable(np.random.randn(pop_size, features), dtype=tf.float32)

# Initialize placeholders
truth_ph = tf.placeholder(tf.float32, [1, features])
crossover_mat_ph = tf.placeholder(tf.float32, [num_children, features])
mutation_val_ph = tf.placeholder(tf.float32, [num_children, features])

# Calculate fitness (MSE)
fitness = -tf.reduce_mean(tf.square(tf.subtract(population, truth_ph)), 1)
top_vals, top_ind = tf.nn.top_k(fitness, k=pop_size)

# Get best fit individual
best_val = tf.reduce_min(top_vals)
best_ind = tf.argmin(top_vals, 0)
best_individual = tf.gather(population, best_ind)

# Get parents
population_sorted = tf.gather(population, top_ind)
parents = tf.slice(population_sorted, [0, 0], [num_parents, features])


# Get offspring
# Indices to shuffle-gather parents
rand_parent1_ix = np.random.choice(num_parents, num_children)
rand_parent2_ix = np.random.choice(num_parents, num_children)
# Gather parents by shuffled indices, expand back out to pop_size too
rand_parent1 = tf.gather(parents, rand_parent1_ix)
rand_parent2 = tf.gather(parents, rand_parent2_ix)
rand_parent1_sel = tf.multiply(rand_parent1, crossover_mat_ph)
rand_parent2_sel = tf.multiply(rand_parent2, tf.subtract(1., crossover_mat_ph))
children_after_sel = tf.add(rand_parent1_sel, rand_parent2_sel)

# Mutate Children
mutated_children = tf.add(children_after_sel, mutation_val_ph)

# Combine children and parents into new population
#new_population = tf.concat(0, [parents, mutated_children])
new_population = tf.concat([parents, mutated_children],0)

step = tf.group(population.assign(new_population))

#init = tf.initialize_all_variables()
init = tf.global_variables_initializer()
sess.run(init)

# Run through generations
for i in range(generations):
    # Create cross-over matrices for plugging in.
    crossover_mat = np.ones(shape=[num_children, features])
    crossover_point = np.random.choice(np.arange(1, features-1, step=1), num_children)
    for pop_ix in range(num_children):
        crossover_mat[pop_ix,0:crossover_point[pop_ix]]=0.
    # Generate mutation probability matrices
    mutation_prob_mat = np.random.uniform(size=[num_children, features])
    mutation_values = np.random.normal(size=[num_children, features])
    mutation_values[mutation_prob_mat >= mutation] = 0
    
    # Run GA step
    feed_dict = {truth_ph: truth.reshape([1, features]),
                 crossover_mat_ph: crossover_mat,
                 mutation_val_ph: mutation_values}
    step.run(feed_dict, session=sess)
    best_individual_val = sess.run(best_individual, feed_dict=feed_dict)
    
    if i % 5 == 0:
       best_fit = sess.run(best_val, feed_dict = feed_dict)
       print('Generation: {}, Best Fitness (lowest MSE): {:.2}'.format(i, -best_fit))

plt.plot(truth, label="Real 5G Slice Traffic")
plt.plot(np.squeeze(best_individual_val), label="Expect 5G Slice Traffic")
plt.axis((0, features, -1.25, 1.25))
plt.legend(loc='upper right')
plt.show()
