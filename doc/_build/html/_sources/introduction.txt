============
Introduction
============

A main goal of this software is to decompose and manage high dimensional data from a variety of sources. The motivation came from the need to parse different tabular data files in varying layouts and formats. The minimum requirements to decompose a file are:

#. A header row is defined which contains a descriptive element for each column.
#. The columns are homogeneous.

The general theory behind how the decomposition works is that each column can be related to a variable in the system. This includes general items like a basis or date, if the data is a time series, and specific items like point of sale or finished goods, that may be domain specific.

Once the data has been extracted from the files, it can be analyzed and assist the user in making decisions. The end game of this software is to be able to make predictions about future values of an independent variable, in this case finished goods. The forecasting models included in this software are multiple linear regression, exponential smoothing, and autoregressive-moving-average. The first model is most useful when the dimensionality is greater than one. The last two will produce better results over a single dimension.
