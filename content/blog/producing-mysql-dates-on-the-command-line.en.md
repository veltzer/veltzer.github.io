+++
title = "Producing MySQL dates on the command line"
description = "A one-line shell alias, date +'%F %T', prints the current date and time in MySQL format for pasting into database editors that will not take SQL."
date = 2010-07-21

[taxonomies]
tags = ["mysql", "linux", "command-line"]
+++

I often find myself in need of inserting data manually into a MySQL database using some kind of database editor. In a database editor you find yourself manually inserting values into cells of a table and in most of them you are not allowed to enter an SQL expression (the MySQL Query Browser is a prime example). In this case I need some way to generate the current date and time as per the MySQL format quickly on the command line. I will usually use:

`alias date_mysql="date +'%F %T'"`
