+++
title = "Database Inheritance: Three Ways to Do It and What Each One Costs"
date = 2012-01-22

[taxonomies]
tags = ["programming", "database"]
+++

Object models have inheritance and relational databases do not, and every application that maps one onto the other has to decide how. There are three standard answers, plus one that PostgreSQL offers natively, and the choice has consequences for constraints, queries, indexes, and the object-relational mapper that will sit on top. I want to lay them out plainly, because the decision is usually made by default and regretted in a year.

Take the usual example. A `Vehicle` has an `id`, an `owner`, and a `registration`. A `Car` adds `doors`; a `Truck` adds `payload_kg`.

## Single-Table Inheritance

One table holds everything, with a column that says which kind of row this is:

```sql
CREATE TABLE vehicle (
    id            SERIAL PRIMARY KEY,
    kind          TEXT NOT NULL CHECK (kind IN ('car', 'truck')),
    owner         TEXT NOT NULL,
    registration  TEXT NOT NULL UNIQUE,
    doors         INTEGER,
    payload_kg    INTEGER
);
```

**Queries are trivial.** Every vehicle is one row in one table; "all vehicles owned by X" is a single scan and "all trucks" is a filter on `kind`. Polymorphic loading needs no joins.

**Constraints are weak.** `doors` must be `NULL` for a truck and `NOT NULL` for a car, and the schema cannot say so without a check constraint per subclass column:

```sql
CHECK ((kind = 'car') = (doors IS NOT NULL)),
CHECK ((kind = 'truck') = (payload_kg IS NOT NULL))
```

That works for two subclasses. For twenty, with ten columns each, the table is mostly `NULL` and the check constraints are a wall of text. The wasted space is rarely the problem; the loss of the schema as documentation is.

**Indexes are shared.** An index on `payload_kg` indexes every car's `NULL` too. Partial indexes (`WHERE kind = 'truck'`) fix that where the database supports them.

This is the mapper's favourite, because it is the easiest to implement, and it is the right choice when the subclasses differ by a few columns and you query across the hierarchy constantly.

## Class-Table Inheritance

One table per class, with the subclass tables holding only their own columns and a foreign key to the parent row:

```sql
CREATE TABLE vehicle (
    id            SERIAL PRIMARY KEY,
    owner         TEXT NOT NULL,
    registration  TEXT NOT NULL UNIQUE
);

CREATE TABLE car (
    id     INTEGER PRIMARY KEY REFERENCES vehicle(id) ON DELETE CASCADE,
    doors  INTEGER NOT NULL
);

CREATE TABLE truck (
    id          INTEGER PRIMARY KEY REFERENCES vehicle(id) ON DELETE CASCADE,
    payload_kg  INTEGER NOT NULL
);
```

**Constraints are exact.** Every column is `NOT NULL` where it should be, the schema reads like the class diagram, and a foreign key to `vehicle(id)` means "any vehicle" while one to `car(id)` means "a car". This is the normalised answer and the one a database person will draw on the whiteboard.

**Queries need joins.** Loading a car is `vehicle JOIN car`. Loading "all vehicles with their subclass data" is a `LEFT JOIN` to every subclass table, or one query per subclass and a merge in the application. Inserting a car is two inserts in a transaction. None of this is hard; all of it is more work per row than the single table, and the mapper will hide it from you until the day you look at the query log.

**One thing the schema cannot say:** that a `vehicle` row has exactly one subclass row, not zero and not two. You can enforce it with a trigger or by putting a `kind` column on `vehicle` and a matching column on each subclass with a composite foreign key. Most people do not bother, and most people eventually find an orphan.

## Concrete-Table Inheritance

One table per concrete class, each carrying all the inherited columns, and no parent table at all:

```sql
CREATE TABLE car (
    id            SERIAL PRIMARY KEY,
    owner         TEXT NOT NULL,
    registration  TEXT NOT NULL UNIQUE,
    doors         INTEGER NOT NULL
);

CREATE TABLE truck (
    id            SERIAL PRIMARY KEY,
    owner         TEXT NOT NULL,
    registration  TEXT NOT NULL UNIQUE,
    payload_kg    INTEGER NOT NULL
);
```

**Each table is self-contained**, which is fast for queries within a class and pleasant for a class that is almost never treated as its parent.

**The parent disappears.** There is no `vehicle` table, so there is nothing for another table to reference when it means "any vehicle". The `UNIQUE` on `registration` is per table, so a car and a truck can share one, and fixing that needs a trigger or an external table. "All vehicles" is a `UNION ALL` across every subclass table, and adding a subclass means changing every such query. The two `SERIAL` sequences also hand out overlapping ids, so `id` alone no longer identifies a vehicle; you need `(kind, id)`, which the mapper will have opinions about.

Use this when the classes share an interface in the code but are genuinely separate things in the data. It is the wrong choice the moment anything needs to point at the parent.

## PostgreSQL's Native Version

PostgreSQL has table inheritance built in:

```sql
CREATE TABLE vehicle (
    id            SERIAL PRIMARY KEY,
    owner         TEXT NOT NULL,
    registration  TEXT NOT NULL UNIQUE
);

CREATE TABLE car (doors INTEGER NOT NULL) INHERITS (vehicle);
CREATE TABLE truck (payload_kg INTEGER NOT NULL) INHERITS (vehicle);
```

A `SELECT * FROM vehicle` returns the rows of `car` and `truck` too, with the parent's columns, and `SELECT * FROM ONLY vehicle` returns only rows inserted directly into the parent. Storage is concrete-table (each child holds its own full rows); querying is single-table (the parent sees everything). It looks like the best of both.

The catch is what does not inherit. **Unique constraints, primary keys, and foreign keys apply per table.** The `UNIQUE (registration)` on `vehicle` does not prevent a car and a truck from sharing a registration, and a foreign key `REFERENCES vehicle(id)` from another table will not accept a car's id, because the car's row is not in `vehicle`'s index. Check constraints and `NOT NULL` do inherit; indexes do not, and must be created on each child. This is documented and it is the reason the feature is used far more for partitioning than for modelling.

## What the Mapper Will Do to You

Every object-relational mapper supports the first two strategies and most support the third; Hibernate calls them `SINGLE_TABLE`, `JOINED`, and `TABLE_PER_CLASS`. Two warnings from experience.

The mapper's default is almost always single-table, because it is the easiest for the mapper. That is not the same as being right for your data.

And the mapper will generate the polymorphic queries for you, which means you will not see the `LEFT JOIN` to twelve subclass tables until it is slow. Decide the strategy by looking at the queries you will actually run, write two of them by hand against each layout, and choose with the query plan in front of you.

## The Rule I Use

Single-table when the subclasses differ by little and cross-hierarchy queries dominate. Class-table when the schema has to be right and the joins are affordable, which is most of the time. Concrete-table when the classes only share code. PostgreSQL's `INHERITS` for partitions, and for modelling only after reading the paragraph about what does not inherit twice.
