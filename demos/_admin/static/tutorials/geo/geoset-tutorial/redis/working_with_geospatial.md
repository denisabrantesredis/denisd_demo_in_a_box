# Restaurant Example

### Introduction

The restaurant dataset contains 100 documents containing examples of restaurants. Besides the coordinates, the following metadata fields were also created for each document:

* ID
* Name
* Address (street)
* Phone
* Cousine (a choice between `'Italian'` , `'Asian'` , `'BBQ'` , `'Pizza'` , `'Breakfast'` and `'Mexican'`)

In this example, we will seach by coordinates, with the option of filtering by metadata.

The <a href="/geodemo">Geodemo</a> page contains a working example of an application that uses the coordinates to display data on a map.

&nbsp;

### Searching for Restaurants

Use the following commands to search for a restaurant near Chicago, IL, USA:

```redis Search by Coordinates

GEOSEARCH "idx:restaurant_geo" FROMLONLAT -94.41551 39.09112 BYRADIUS 130 M

```



&nbsp;



# Basic Commands

* [GEOADD](https://redis.io/commands/geoadd/) adds a location to a given geoset (note that longitude comes before latitude with this command).
* [GEOSEARCH](https://redis.io/commands/geosearch/) returns locations with a given radius or a bounding box.

You can find the full list of commands [here](https://redis.io/commands/?group=geo)

## Examples

Add a few drivers to Geoset

```redis Add locations

GEOADD drivers -81.379234 28.538336 driver1
GEOADD drivers -81.407570 28.291956 driver2
GEOADD drivers -81.274948 28.807674 driver3

```

```redis Get positions of some drivers

GEOPOS drivers driver1 driver2

```

Find all drivers within a 5 kilometer radius of a given location, and return the distance to each driver:

```redis Find drivers by radius

GEOSEARCH drivers FROMLONLAT -81.379234 28.538336 BYRADIUS 500 km WITHDIST ASC
GEOSEARCH drivers FROMLONLAT -81.379234 28.538336 BYRADIUS 200 km WITHCOORD

```

Find all drivers within a 50 kilometer radius of a member of the geo set, and return the distance

```redis Find drivers from driver1

GEOSEARCH drivers FROMMEMBER driver1 BYRADIUS 5 km WITHDIST

```

Find all drivers within a box of a given location, and return the distance to each driver

```redis Find drivers by box

GEOSEARCH drivers FROMLONLAT -81.379234 28.538336 BYBOX 400 400 km ASC WITHCOORD WITHDIST

```

Delete driver inside geo set

```redis Delete driver

ZREM drivers driver1

```

Delete key with DEL or UNLINK command

```redis Delete key

DEL drivers
UNLINK drivers

```
