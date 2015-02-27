#!/usr/bin/python

"""
SQLite Database Interface for Information

Copyright (C) 2014, 2015 by Andrew Chalres Hawkins

This file is part of Forsteri.

Forsteri is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Forsteri is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Forsteri.  If not, see <http://www.gnu.org/licenses/>.
"""

"""
Import Declarations
"""
import datetime as dt
import re
import sqlite3

"""
Constant Declarations
"""
DATA = "/home/andrew/Dropbox/product-quest/Forsteri/data/"
MASTER = ''.join([DATA, "master.db"])

"""
Product Information
"""
def getAttribute(attribute, connection=None):
    """
    Get all values for a single attribute.

    Args:
      attribute (str): The attribute to pull from the database.
      connection (sqlite3.Connection, optional): A connection to the database.

    Returns:
      list of str: The attributes across all tuples.
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to retrieve all items under attribute.
    cursor.execute("""SELECT {a} FROM information;""".format(a=attribute))

    # Fetch all rows.
    products = cursor.fetchall()

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.close()

    return products

def getAllData(connection=None):
    """
    Get all data from the database.

    Args:
      connection (sqlite3.Connection, optional): A connection to the database.

    Returns:
      list of list of str: The data for all tuples and attributes.
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to retrieve all data.
    cursor.execute("""SELECT product, sku, account, class, category, 
subcategory FROM information;""")

    # Fetch all rows.
    productData = cursor.fetchall()

    # Convert all None values to be empty strings.
    productData = ['' if attribute is None else attribute for product in\
        productData for attribute in product]
    productData = [productData[z : z + 6] for z in range(0,
        len(productData), 6)]

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.close()

    return productData

def getData(sieve, connection=None):
    """
    Get the data after filtering with a sieve.

    Args:
      sieve (dict of str: str): 
      connection (sqlite3.Connection, optional): 

    Returns:
      list of list of str: The data for tuples and attributes satifying the
        filter.
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Define the sieve string.
    sieveStr = ''
    for (key, value) in sieve.items():
        if value != '' and value is not None:
            if key == "product" or key == "sku":
                sieveStr = ''.join([sieveStr, " AND ", key, " LIKE '", value,
                    "%'"])
            else:
                sieveStr = ''.join([sieveStr, " AND ", key, "='", value, "'"])


    # If the string is length zero, no sieve was input.
    if len(sieveStr) == 0:
        # Execute the statement to retrieve all data.
        cursor.execute("""SELECT product, sku, account, class, category, 
subcategory FROM information;""")
    else:
        # Cut the beginning of the string.
        sieveStr = sieveStr[5:]

        # Execute the statement to retrieve the sieve's information.
        cursor.execute("""SELECT product, sku, account, class, category, 
subcategory FROM information WHERE {s};""".format(s=sieveStr))

    # Fetch all rows.
    productData = cursor.fetchall()

    # Convert all None values to be empty strings.
    productData = ['' if attr is None else attr for product in productData for\
        attr in product]
    productData = [productData[z : z + 6] for z in range(0, len(productData),
        6)]

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.close()

    return productData

def getProduct(product, connection=None):
    """
    Get the data for a single product.

    Args:
      product (str): The name of the product.
      connection (sqlite3.Connection, optional): A connection to the database.

    Returns:
      list of str: The data for a single tuple.
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to retrieve the product's information.
    cursor.execute("""SELECT product, sku, account, class, category, 
subcategory FROM information WHERE product='{p}';""".format(p=product))

    # Fetch the first responded row.
    productData = cursor.fetchone()

    # Change None to be an empty string.
    productData = ['' if attr is None else attr for attr in productData]

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.close()

    return productData

def addProduct(productData, connection=None):
    """
    Add a product tuple to the database.

    Args:
      productData (dict of {str: str}): A tuple to add to the database. Must
        be of the form {"product": ?, "sku": ?, "account": ?, "class": ?,
        "category": ?, "subcategory": ?}.
      connection (sqlite3.Connection, optional): A connection to the database.

    Returns:
      bool: True if successful, false otherwise.
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Check if the product has been input or if it has already been added.
    if "product" not in productData.keys():
        return False

    # Initlialize the attribute and value lists.
    attrs = []
    values = []

    # Iterate over the inputted values and extract attributes.
    for (key, value) in productData.items():
        if value is None or value == '':
            continue
        else:
            attrs.append(key)
            values.append(value)

    # Convert to a valid string removing unnecessary characters.
    if len(attrs) == 1:
        attrs = re.sub("[',]", '', str(tuple(attrs)))
        values = re.sub(",", '', str(tuple(values)))
    else:
        attrs = re.sub("'", '', str(tuple(attrs)))
        values = str(tuple(values))

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the command to write the new data to the database.
    try:
        cursor.execute("""INSERT INTO information {a} VALUES {v}""".\
            format(a=attrs, v=values))
    except IntegrityError:
        print(productData["product"] + " already exists in the database.")

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def addProducts(newProducts, data, overwrite=False, connection=None):
    """
    Add many product tuples to the database.

    Args:
      newProducts (list of str): The list of new products.
      data (list of dict of str: str): The list of new data housed in
        dictionaries in the form {"product": ?, "sku": ?, "account": ?,
        "class": ?, "category": ?, "subcategory": ?}.
      overwrite (bool, optional): True if data already in the database
        should be overwritten with the new data, false otherwise.
      connection (sqlite3.Connection, optional): A connection to the database.

    Returns:
      bool: True if successful, false otherwise.
    """

    # Get the list of old products.
    oldProducts = getAttribute("product", connection)

    # Convert the new products to be a set.
    newProductsSet = set(newProducts)

    # Find the difference between the old and new data.
    addProducts = newProductsSet.difference(oldProducts)

    # Find the intersection of the old and new data.
    setProducts = newProductsSet.intersection(oldProducts)

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Iterate over the rows in the input data.
    for productData in data:
        if productData["product"] in addProducts:
            # Initlialize the attribute and value lists.
            attrs = []
            values = []

            # Iterate over the inputted values and extract attributes.
            for (key, value) in productData.items():
                if value is None or value == '':
                    continue
                else:
                    attrs.append(key)
                    values.append(value)

            # Convert to a valid string removing unnecessary characters.
            if len(attrs) == 1:
                attrs = re.sub("[',]", '', str(tuple(attrs)))
                values = re.sub(",", '', str(tuple(values)))
            else:
                attrs = re.sub("'", '', str(tuple(attrs)))
                values = str(tuple(values))

            # Execute the command to write the new data to the database.
            cursor.execute("""INSERT INTO information {a} VALUES {v}""".\
                format(a=attrs, v=values))
        elif overwrite:
            # Set up the product for input
            productInput = "'" + productData["product"] + "'"

            # Iterate over the inputted values and update then in the database.
            for (key, value) in productData.items():
                change = key + "='" + value + "'"
                cursor.execute("""UPDATE information SET {c} WHERE product={p}
""".format(c=change, p=productInput))

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def getProductHash(connection=None):
    """
    """

    # 
    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the command to pull all products that do not have a null sku.
    cursor.execute("""SELECT product, sku FROM information WHERE sku IS NOT 
NULL""")

    # Fetch all of the returned data.
    data = cursor.fetchall()

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.close()

    # Convert the data to a dictionary.
    match = {x[1]: x[0] for x in data}

    return match

def setProduct(product, productData, connection=None):
    """
    Set a product's tuple in the database.

    Args:
      product (str): The product currently in the database.
      productData (dict of {str: str}): A tuple to add to the database. Must
        be of the form {"product": ?, "sku": ?, "account": ?, "class": ?,
        "category": ?, "subcategory": ?}. Use None to set attributes to be
        NULL.
      connection (sqlite3.Connection, optional): A connection to the database.

    Returns:
      bool: True if successful, false otherwise.
    """

    # Check if the product is in the database.
    if product not in getAttribute("product", connection):
        return False

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    productInput = "'" + product + "'"

    # Iterate over the input product data dictionary.
    for (key, value) in productData.items():
        if value == '':
            change = key + "=NULL"
        else:
            change = key + "='" + value + "'"
        cursor.execute("""UPDATE information SET {c} WHERE product={p}""".\
            format(c=change, p=productInput))

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def setProducts(products, productData, connection=None):
    """
    Set a group of product's to have the same tuple (except unique) in the
    database.

    Args:
      product (str): The product currently in the database.
      productData (dict of {str: str}): A tuple to add to the database. Must
        be of the form {"product": ?, "sku": ?, "account": ?, "class": ?,
        "category": ?, "subcategory": ?}. Use None to set attributes to be
        NULL.
      connection (sqlite3.Connection, optional): A connection to the database.

    Returns:
      bool: True if successful, false otherwise.
    """

    # Check if product or sku is defined in the input data, if so return false.
    if productData["product"] != '' or productData["sku"] != '':
        return False

    # Define the input string for all products.
    change = ''
    for (key, value) in productData.items():
        if value != '':
            change = ''.join([change, ", ", key, "='", value, "'"])

    change = change[2:]

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Iterate over the inputted products and change the data.
    for product in products:
        product = "'" + product + "'"
        cursor.execute("""UPDATE information SET {c} WHERE product={p}""".\
            format(c=change, p=product))

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def removeProduct(product, connection=None):
    """
    Remove a product tuple from the database.

    Args:
      products (str): The product to be removed from the database.
      connection (sqlite3.Connection, optional): A connection to the database.

    Returns:
      bool: True if successful, false otherwise.
    """

    # Convert to a valid string by adding or removing characters.
    product = "'" + product + "'"

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the command to remove the row of the given product.
    cursor.execute("""DELETE FROM information WHERE product={p}""".\
        format(p=product))

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

"""
Missing Products
"""
def addMissing(basis, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the command to add a missing product.
    cursor.execute("""INSERT OR IGNORE INTO missing (basis) VALUES ('{b}')""".\
        format(b=basis))

    # Execute teh command to get the id of the input basis.
    cursor.execute("""SELECT id FROM missing WHERE basis='{b}'""".\
        format(b=basis))

    # Fetch the returned id.
    basisID = cursor.fetchone()[0]

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return basisID

"""
Import Information
"""
def addImport(fileInfo, connection=None):
    """
    """

    # Put the inputs into the correct string form.
    columns = str(tuple(fileInfo.keys())).replace("'", '')
    values = str(tuple(fileInfo.values()))

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to add the import information.
    cursor.execute("""INSERT INTO import {c} VALUES {v}""".format(c=columns,
        v=values))

    # Execute the statement to get the id of the input.
    cursor.execute("""SELECT id FROM import WHERE date_of_import='{doi}'""".\
        format(doi=fileInfo["date_of_import"]))

    # Fetch the returned id.
    importID = cursor.fetchone()[0]

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return importID

"""
Link Products
"""
def addLink(old, new, connection=None):
    """
    """

    # Create the string form for the values.
    values = str((old, new))

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to add the link.
    cursor.execute("""INSERT OR REPLACE INTO link (old, new) VALUES {v}""".\
        format(v=values))

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def setLink(old, new, kind, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to add the link.
    if kind == 1:
        cursor.execute("""UPDATE link SET old='{o}' WHERE new='{n}'""".\
            format(o=old, n=new))
    elif kind == 2:
        cursor.execute("""UPDATE link SET new='{n}' WHERE old='{o}'""".\
            format(o=old, n=new))
    else:
        cursor.execute("""UPDATE link SET old='{o}', new='{n}' WHERE
old='{o2}'""".format(o=old, n=new, o2=kind))

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def removeLink(old, new, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to delete the input link.
    cursor.execute("""DELETE FROM link WHERE old='{o}' AND new='{n}'""".\
        format(o=old, n=new))

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def getLinks(connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to add the link.
    cursor.execute("""SELECT old, new FROM link ORDER BY old""")

    # Fetch all of the returned data.
    links = cursor.fetchall()

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.close()

    return links

def getLinksTo(product, connection=None):
    """
    Assumes links are one to one.
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Initialize links.
    links = []

    # Execute the command to 
    cursor.execute("""SELECT old FROM link WHERE new='{n}'""".\
        format(n=product))

    # Fetch all of the returned data.
    prelink = [x[0] for x in cursor.fetchall()]

    # Iterate until no values are returned.
    while len(prelink) != 0:
        print(prelink)
        if len(prelink) == 1:
            links.append(prelink[0])
            cursor.execute("""SELECT old FROM link WHERE new='{n}'""".\
                format(n=product))
            prelink = [x[0] for x in cursor.fetchall()]
        else:
            for link in prelink:
                t = getLinksTo(link, connection)
                links.extend(t)
            break

    # Close the cursor.
    cursor.close()

    # Commit the change to the database and close the connection.
    if flag:
        connection.close()

    return links

"""
Helper Functions
"""
def text2date(text):
    """
    SQL text date format is yyyy-mm-dd.
    """

    # 
    return dt.date(int(text[0 : 4]), int(text[5 : 7]), int(text[8 : 10]))
