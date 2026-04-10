---
tags:
  - mysql
  - linux
  - command-line
date: 2010-07-21
---

# Producing MySQL dates on the command line

I often find myself in need of inserting data manually into a MySQL database using some kind of database editor. In a database editor you find yourself manually inserting values into cells of a table and in most of them you are not allowed to enter an SQL expression (the MySQL Query Browser is a prime example). In this case I need some way to generate the current date and time as per the MySQL format quickly on the command line. I will usually use:

`alias date_mysql="date +'%F %T'"`
