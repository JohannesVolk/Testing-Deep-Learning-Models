# Testing Deep Learning Models

This project was part of the 2021 [Advanced Software Testing seminar](https://www.cs.cit.tum.de/sse/lehre/software-qualitaet/) at the Technical University of Munich. 

The goal of this seminar paper was to compare compares recent methodologies for testing Deep
Learning models among themselves and other more traditional software
testing approaches.
In the first part a short introduction to feedforward neural networks is given and
different properties relevant to testing these systems are explained and illustrated with examples.
In the second part the presented concepts are applied by putting the robustness of an [open-source MNIST classification model](https://github.com/dangeng/Simple_Adversarial_Examples) to the test.

Disclaimer:
- the code for model and adversarial generation originates from this repository and was adapted for this project
- it is kept as simple as possible and doesn't use a framework like PyTorch or Tensorflow in order to control every part of the model to the fullest

Further, [recently proposed](https://arxiv.org/abs/2101.12100) neuron activation metrics for adversarial attack detection are explored and re-implemented.

# Application

## Pipeline

One can capture live footage of handwritten digits with a camera (e.g. smartphone).
These digits are processed and put into a format the neural network can use.

| raw capture | cropping & normalizing | treshhold filter |
|---------|------------------------------|------------------|
| <img src="imgs/unprocessed.png" width="250" height="250" />    |  <img src="imgs/processing1.png" width="250" height="250" /> | <img src="imgs/processing2.png" width="250" height="250" /> |

The model will predict these digits with high accuracy as they are very similar to the ones in the MNIST dataset.

## The Problem with Adversarial Attacks

When one creates an so called adversarial attack even a model with high accuracy can be fooled as the robustness of a model is not easily determined.

For example a digit five, displayed below, is merged with an attack pattern that fools the model.
This attack pattern is constructed with back-propagation in a way that the model classifies it with a label of ones choosing without the need to be resembling the class at all.
([read this](https://christophm.github.io/interpretable-ml-book/adversarial.html) for a more detailed introduction of adversarial examples)

The resulting image gets misclassified with high probability on the wrong label.


| source img | attack pattern | finished adversarial example |
|---------|------------------------------|------------------|
| <img src="imgs/source.png" width="250" height="250" />    |  <img src="imgs/attackPattern.png" width="250" height="250" /> | <img src="imgs/adversarial.png" width="250" height="250" /> |



This can be a severe problem for other applications of Deep Learning for example in Traffic Sign Classification (e.g. see this research project).

## Confidence through Analysis of Neuron Coverage

In 2021 Guilio et al. proposed [a novel approach](https://arxiv.org/abs/2101.12100) to increase the confidence of DNN's by analyzing the coverage of the neurons in forward passes during developement.

The idea is to document how different input classes activate the individiual neurons differently.
For each class an aggregated pattern is constructed according to a so called "Coverage Analysis Methods" (e.g. interval of all observed values). For more details please take a look at my seminar paper or the original paper.
The hypothesis is that adverserial attacks cause unusual activity within the neurons and an attack could be detected.

In the plot below one can see the difference in neural activity between the pre-recorded activation range and the live-values within the forward pass of the corresponding example. Example a) is captured and instantly and b) is the adversarial attack generated out of a).

<center><img src="imgs/detection.png" width="750" height="750" /></center>

One could conclude that the adversarial attack in the bottom image causes high deviation from the recorded behaviour that is usually seen with other images of the predicted class.

## Conclusion

The results show that the approach of Guilio et al. is able to detect adversarial attacks in context of the MNIST digit classification.
Therfore traditional testing metrics like test coverage could be translated to the domain of Deep Learning.
By taking a look inside the black box, neuron coverage might reveal relevant insights in the working of DNN's and make AI more understandable.









