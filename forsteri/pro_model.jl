using Dates
using SQLite

LOC = "/home/andrew/Dropbox/product-quest/Forsteri/data/"
DATA = LOC * "data.db"
MASTER = LOC * "master.db"

dataDB = SQLiteDB(DATA)
masterDB = SQLiteDB(MASTER)

### Run All Functions
function runMLR(products=None)
    if products == None
        products = getProductNames()
    end

    data3 = Dict{ASCIIString, Array{Any,2}}()
    for product in products
        variables = hasVariables(product)

        data = getData(product, variables)

        data2 = curtail(data)

        for key in keys(data2)
            data3[key] = overlap(data2[key])
        end
    end

    dataAll = Array(Float64, size(data3["finished_goods_monthly"])[1],
        length(data3), 12)
    for variable in keys(data3)
        for i = 1 : 12
            dataAll[, , i] = hcat(data3[variable][:, i])
        end
    end

    return data3
end

### Model Functions
function mLR(dep, ind)
    ind = hcat(ones(size(ind)[1]), ind)
    beta = pinv(ind' * ind) * inv' * dep

    return beta
end

### Helper Functions
function getProductNames()
    return query(masterDB, "SELECT DISTINCT product FROM information")[1]
end

function hasVariables(product)
    variables = query(dataDB,
        "SELECT name FROM sqlite_master WHERE type='table'")[1]

    has = []
    for variable in variables
        if variable[end - 7 : end] == "_monthly"
            value = query(dataDB, "SELECT DISTINCT product FROM " * variable *
                " WHERE product='" * product * "'")[1][1]
            if value == product
                has = vcat(has, variable)
            end
        end
    end

    return has
end

function getData(product, variables)
    second = " WHERE product='" * product * "' ORDER BY date"

    data = Dict{ASCIIString, Array{Any,2}}()
    for variable in variables
        dataInter = convert(Matrix, query(dataDB,
            "SELECT date, value FROM " * variable * second))
        dataInter[:, 1] = [Date(x) for x in dataInter[:, 1]]
        data[variable] = dataInter
    end

    return data
end

function overlap(data)
    firstYear = year(data[1, 1])
    firstMonth = month(data[1, 1])
    lastYear = year(data[end, 1])
    lastMonth = month(data[end, 1])

    data2 = copy(data)

    if firstMonth != 1
        for x = firstMonth - 1 : -1 : 1
            data2 = vcat([Date(firstYear, x, 1) NaN], data2)
        end
    end

    if lastMonth != 12
        for x = lastMonth + 1 : 12
            data2 = vcat(data2, [Date(lastYear, x, 1) NaN])
        end
    end

    return reshape(data2[:, 2], 12, lastYear - firstYear + 1)'
end

function curtail(data)
    starts = []
    ends = []
    for key in keys(data)
        starts = vcat(starts, data[key][1, 1])
        ends = vcat(ends, data[key][end, 1])
    end

    first = maximum(starts)
    last = minimum(ends)

    dataNew = Dict{ASCIIString, Array{Any,2}}()
    for key in keys(data)
        temp = [None None]
        for i = 1 : size(data[key])[1]
            if data[key][i, 1] < first || data[key][i, 1] > last
                pass
            else
                temp = vcat(temp, data[key][i, :])
            end
        end
        dataNew[key] = temp[2 : end, :]
    end

    return dataNew
end
