#!/bin/python

# NOTE: It is encapsulated package data

class Package(object):
    def __init__(
            self,
            name,
            description,
            category,
            subcategory,
            subcategory_description,
            version,
    ):
        self.name = name
        self.description = description
        self.category = category
        self.subcategory = subcategory
        self.subcategory_description = subcategory_description
        self.version = version