#=
Moving Averages 

This file contains the algorithms used to calculate many types of moving
averages.

Needs:
  StatsBase

Examples:
  movAvg = ama(x, 15, false)

To Do:
  
=#

using StatsBase

function ama(x::Array{Float64,1}, period::Int64; pad::Bool=true)
    #=
    This function determines the arithmetic (simple) moving average of a
    dataset using a subset of data.

    Args:
      x (Array{Float64,1}): The data to be used for calculation. Newest data
        should be at the end of the array.
      period (Int64): The size of the window used for average calculations.
      pad (Bool, optional): Fill the missing data with NaN to keep the input
        and output the same length.

    Returns:
      Array{Float64,1}: The arithmetic moving average values.
    =#

    # Initialize commonly used values.
    xLength = length(x)
    maLength = xLength - period + 1
    ma = zeros(maLength)

    # Catch input errors
    if period < 1 || period > xLength
        error("ama: period must be between 1 and the length of x.")
    end

    # Detrmine the arithmetic moving average using the fast algorithm.
    ma[1] = mean(x[1 : period])
    for i = 2 : maLength
        ma[i] = ma[i - 1] + (x[i + period - 1] - x[i - 1]) / period
    end

    # Pad the beggining of the moving average with NaNs.
    if pad == true
        ma = vcat(fill(NaN, period - 1), ma)
    end

    # Return the arithmetic moving average.
    return ma
end

function cma(x::Array{Float64,1})
    #=
    This function determines the cumulative moving average of a dataset by
    using all previous values for each calculation.

    Args:
      x (Array{Float64,1}): The data to be used for calculation. Newest data
        should be at the end of the array.

    Returns:
      Array{Float64,1}: The cumulative moving average values.
    =#

    # Initlialize commonly used variables.
    xLength = length(x)
    ma = zeros(xLength)

    # Determine the cumulative moving average using the fast algorithm.
    ma[1] = x[1]
    for i = 2 : xLength
        ma[i] = (x[i] + (i - 1) * ma[i - 1]) / i
    end

    # Return the cumulative moving average.
    return ma
end

function dema(x::Array{Float64,1}, alpha::Float64, beta::Float64; pad::Bool=true)
    #=
    This function determines the double exponential moving average of a
    dataset by ...

    Args:
      x (Array{Float64,1}): The data to be used for calculation. Newest data
        should be at the end of the array.
      alpha (Float64): The smoothing factor.

    Returns:
      Array{Float64,1}: The cumulative moving average values.

    =#

    # Initlialize commonly used variables.
    xLength = length(x)
    maLength =  xLength - 1
    ma = zeros(maLength)
    s = zeros(maLength)
    b = zeros(maLength)

    s[1] = x[2]
    b[1] = x[2] - x[1]
    for i = 3 : xLength
        s[i] = alpha * (x[i] - s[i - 1] - b[i - 1]) + s[i - 1] + b[i - 1]
        b[i] = beta * (s[i] - s[i - 1] - b[i - 1]) + b[i - 1]
        ma[i]
    end

    return NaN
end

function ema(x::Array{Float64,1}, alpha::Number)
    #=
    This function determines the exponential moving average of a dataset by
    applying a weight to the difference of the previous average and new
    observation.

    Args:
      x (Array{Float64,1}): The data to be used for calculation. Newest data
        should be at the end of the array.
      alpha (Number): The smoothing factor or, if greater than 1, the value
        used to determine the smoothing factor.

    Returns:
      Array{Float64,1}: The cumulative moving average values.
    =#

    # Initlialize commonly used variables.
    xLength = length(x)
    ma = zeros(xLength)
    if alpha > 1
        alpha = 2 / (alpha + 1)
    end

    # Catch input errors
    if alpha < 0
        error("ema: alpha must be greater than 0.")
    end

    # Determine the exponential moving average using the fast algorithm.
    ma[1] = x[1]
    for i = 2 : xLength
        ma[i] = ma[i - 1] + alpha * (x[i] - ma[i - 1])
    end

    # Return the cumulative moving average.
    return ma
end

function gma(x::Array{Float64,1}, period::Int64, pad::Bool=true)
    #=
    This function determines the geometric moving average of a dataset
    using a subset of data.

    Args:
      x (Array{Float64,1}): The data to be used for calculation. Newest data
        should be at the end of the array.
      period (Int64): The size of the subset used for average calculations.
      pad (Bool, optional): Fill the missing data with NaN to keep the input
        and output the same length.

    Returns:
      Array{Float64,1}: The geometric moving average values.
    =#

    # Initialize commonly used values.
    xLength = length(x)
    maLength = xLength - period + 1
    ma = zeros(maLength)

    # Determine the geometric moving average using the fast algorithm.
    ma[1] = geomean(x[1 : period])
    for i = 2 : maLength
        ma[i] = ma[i - 1] * (x[i + period - 1] / x[i - 1]) ^ (1 / period)
    end

    # Pad the beggining of the moving average with NaNs.
    if pad == true
        ma = vcat(fill(NaN, period - 1), ma)
    end

    # Return the geometric moving average.
    return ma
end

function hma(x::Array{Float64,1}, period::Int64, pad::Bool=true)
    #=
    This function determines the harmonic moving average of a dataset
    using a subset of data.

    Args:
      x (Array{Float64,1}): The data to be used for calculation. Newest data
        should be at the end of the array.
      period (Int64): The size of the subset used for average calculations.
      pad (Bool, optional): Fill the missing data with NaN to keep the input
        and output the same length.

    Returns:
      Array{Float64,1}: The harmonic moving average values.
    =#

    # Initialize commonly used values.
    xLength = length(x)
    maLength = xLength - period + 1
    ma = zeros(maLength)

    # Determine the harmonic moving average using the fast algorithm.
    ma[1] = harmmean(x[1 : period])
    for i = 2 : maLength
        ma[i] = period / ((period / ma[i - 1]) + (1 / x[i + period - 1]) - (1 / x[i - 1]))
    end

    # Pad the beggining of the moving average with NaNs.
    if pad == true
        ma = vcat(fill(NaN, period - 1), ma)
    end

    # Return the harmonic moving average.
    return ma
end

function wma(x::Array{Float64,1}, period::Int64, pad::Bool=true)
    #=
    This function determines the weighted moving average of a dataset
    using a subset of data.

    Args:
      x (Array{Float64,1}): The data to be used for calculation. Newest data
        should be at the end of the array.
      period (Int64): The size of the subset used for average calculations.
      pad (Bool, optional): Fill the missing data with NaN to keep the input
        and output the same length.
    
    Returns:
      Array{Float64,1}: The weighted moving average values.
    =#

    # Initlialize commonly used variables.
    xLength = length(x)
    maLength = xLength - period + 1
    tot = zeros(maLength)
    num = zeros(maLength)
    ma = zeros(maLength)
    den = period * (period + 1) / 2

    # Determine the weighted moving average using the fast algorithm.
    tot[1] = sum(x[1 : period])
    num[1] = sum(x[1 : period] .* [1 : period])
    ma[1] = num[1] / den
    for i = 2 : maLength
        tot[i] = tot[i - 1] + x[i + period - 1] - x[i - 1]
        num[i] = num[i - 1] + period * x[i + period - 1] - tot[i - 1]
        ma[i] = num[i] / den
    end

    # Pad the beggining of the moving average with NaNs.
    if pad == true
        ma = vcat(fill(NaN, period - 1), ma)
    end

    # Return the weighted moving average.
    return ma
end
