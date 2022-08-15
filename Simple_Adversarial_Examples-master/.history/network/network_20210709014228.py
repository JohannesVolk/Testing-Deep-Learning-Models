"""
network.py
~~~~~~~~~~

A module to implement the stochastic gradient descent learning
algorithm for a feedforward neural network.  Gradients are calculated
using backpropagation.  Note that I have focused on making the code
simple, easily readable, and easily modifiable.  It is not optimized,
and omits many desirable features.
"""

#### Libraries
# Standard library
import random
from time import sleep
from typing import List

# Third-party libraries
import cupy as cp
import numpy as np

import time

class Network(object):


    def __init__(self, sizes):
        """The list ``sizes`` contains the number of neurons in the
        respective layers of the network.  For example, if the list
        was [2, 3, 1] then it would be a three-layer network, with the
        first layer containing 2 neurons, the second layer 3 neurons,
        and the third layer 1 neuron.  The biases and weights for the
        network are initialized randomly, using a Gaussian
        distribution with mean 0, and variance 1.  Note that the first
        layer is assumed to be an input layer, and by convention we
        won't set any biases for those neurons, since biases are only
        ever used in computing the outputs from later layers."""
        self.num_layers = len(sizes)
        self.sizes = sizes
        self.biases = [cp.random.randn(y, 1) for y in sizes[1:]]
        self.weights = [cp.random.randn(y, x) for x, y in zip(sizes[:-1], sizes[1:])]

    def adversarial(self, n):
        goal = cp.zeros((10, 1))
        goal[n] = 1

        x = cp.random.normal(.5, .3, (784, 1))

        for _ in range(10000):
            d = self.input_derivative(x,goal)
            x -= .01 * d

        return x

    def feedforward(self, a, layers):
        """Return the output of the network if ``a`` is input."""
        a = a.reshape((len(a),1))
        for i in range(0,layers):
            #print(cp.shape(self.weights[i]))
            #print("-----------------------")
            #print(cp.shape(self.biases[i]))
            # print("-----------------------")
            #print(np.shape(a))
            #print("-----------------------")
            #print(cp.shape(cp.dot(self.weights[i], a)))
            #print("-----------------------")

            a = sigmoid(np.dot(self.weights[i], a) + self.biases[i])
            #print(cp.shape(a))
            #sleep(100)
        return a

    def SGD(self, training_data, epochs, mini_batch_size, eta,
            test_data=None,layers=2):
        """Train the neural network using mini-batch stochastic
        gradient descent.  The ``training_data`` is a list of tuples
        ``(x, y)`` representing the training inputs and the desired
        outputs.  The other non-optional parameters are
        self-explanatory.  If ``test_data`` is provided then the
        network will be evaluated against the test data after each
        epoch, and partial progress printed out.  This is useful for
        tracking progress, but slows things down substantially."""
        if test_data: 
            data, l = test_data
            n_test = len(data)
        data, label = training_data
        n = len(label)
        for j in range(epochs):
            start = time.time()
            
            random_order = random.sample(range(0, n), n)

            for k in range(0, n, mini_batch_size):

                self.update_mini_batch(random_order[k:k+mini_batch_size],data,label, eta)

            if test_data:
                print("Epoch {0}: {1} / {2} in {3}".format(
                    j, self.evaluate(test_data,layers), n_test, time.time() - start))
            else:
                print("Epoch {0} complete".format(j))

    def update_mini_batch(self, batch, data, label, eta):
        """Update the network's weights and biases by applying
        gradient descent using backpropagation to a single mini batch.
        The ``mini_batch`` is a list of tuples ``(x, y)``, and ``eta``
        is the learning rate."""
        nabla_b = [cp.zeros(b.shape) for b in self.biases]
        nabla_w = [cp.zeros(w.shape) for w in self.weights]


        for i in batch:
            delta_nabla_b, delta_nabla_w = self.backprop(data[i], label[i])
            for j in range(0,len(nabla_b)):
                nabla_b[j] = cp.add(nabla_b[j],delta_nabla_b[j])

            for j in range(0,len(nabla_w)):
                nabla_w[j] = cp.add(nabla_w[j],delta_nabla_w[j])

            #nabla_w = [nw+dnw for nw, dnw in zip(nabla_w, delta_nabla_w)]

        eta_len = eta/len(batch)

        for i in range(0,len(nabla_w)):
            self.weights[i] = self.weights[i]-eta_len*nabla_w[i]

        for i in range(0,len(nabla_b)):
            self.biases[i] = self.biases[i]-eta_len*nabla_b[i]

        #self.weights = [w-(eta/len(batch))*nw
        #                for w, nw in zip(self.weights, nabla_w)]
        #self.biases = [b-(eta/len(batch))*nb
        #                for b, nb in zip(self.biases, nabla_b)]

    def backprop(self, x, y):
        """Return a tuple ``(nabla_b, nabla_w)`` representing the
        gradient for the cost function C_x.  ``nabla_b`` and
        ``nabla_w`` are layer-by-layer lists of numpy arrays, similar
        to ``self.biases`` and ``self.weights``."""
        nabla_b = [cp.zeros(b.shape) for b in self.biases]
        nabla_w = [cp.zeros(w.shape) for w in self.weights]
        # feedforward
        activation = x
        activations = [x] # list to store all the activations, layer by layer
        zs = [] # list to store all the z vectors, layer by layer
        for b, w in zip(self.biases, self.weights):
            z = cp.dot(w, activation)+b
            zs.append(z)
            activation = sigmoid(z)
            activations.append(activation)
        # backward pass
        delta = self.cost_derivative(activations[-1], y) * \
            sigmoid_prime(zs[-1])
        nabla_b[-1] = delta

        nabla_w[-1] = cp.dot(delta, activations[-2].transpose())

        for l in range(2, self.num_layers):
            z = zs[-l]
            sp = sigmoid_prime(z)
            delta = cp.dot(self.weights[-l+1].transpose(), delta) * sp
            nabla_b[-l] = delta
            nabla_w[-l] = cp.dot(delta, activations[-l-1].transpose())
        return (nabla_b, nabla_w)

    def input_derivative(self, x, y):
        """ Calculate derivatives wrt the inputs"""
        nabla_b = [cp.zeros(b.shape) for b in self.biases]
        nabla_w = [cp.zeros(w.shape) for w in self.weights]
        # feedforward
        activation = x
        activations = [x] # list to store all the activations, layer by layer
        zs = [] # list to store all the z vectors, layer by layer
        for b, w in zip(self.biases, self.weights):
            z = cp.dot(w, activation)+b
            zs.append(z)
            activation = sigmoid(z)
            activations.append(activation)
        # backward pass
        delta = self.cost_derivative(activations[-1], y) * \
            sigmoid_prime(zs[-1])
        nabla_b[-1] = delta
        nabla_w[-1] = cp.dot(delta, activations[-2].transpose())
        # Note that the variable l in the loop below is used a little
        # differently to the notation in Chapter 2 of the book.  Here,
        # l = 1 means the last layer of neurons, l = 2 is the
        # second-last layer, and so on.  It's a renumbering of the
        # scheme in the book, used here to take advantage of the fact
        # that Python can use negative indices in lists.
        for l in range(2, self.num_layers):
            z = zs[-l]
            sp = sigmoid_prime(z)
            delta = cp.dot(self.weights[-l+1].transpose(), delta) * sp
            nabla_b[-l] = delta
            nabla_w[-l] = cp.dot(delta, activations[-l-1].transpose())
        return self.weights[0].T.dot(delta)

    def evaluate(self, test_data,layers):
        """Return the number of test inputs for which the neural
        network outputs the correct result. Note that the neural
        network's output is assumed to be the index of whichever
        neuron in the final layer has the highest activation."""

        data, label = test_data
        maxarg = cp.apply_along_axis(lambda x: cp.argmax(self.feedforward(x,layers)), 1 , data)

        return cp.count_nonzero(cp.equal(cp.equal(maxarg.reshape(len(maxarg)), label), label))

    def cost_derivative(self, output_activations, y):
        """Return the vector of partial derivatives \partial C_x /
        \partial a for the output activations."""
        return (output_activations-y)

#### Miscellaneous functions
def sigmoid(z):
    """The sigmoid function."""
    return 1.0/(1.0+cp.exp(-z))

def sigmoid_prime(z):
    """Derivative of the sigmoid function."""
    return sigmoid(z)*(1-sigmoid(z))
