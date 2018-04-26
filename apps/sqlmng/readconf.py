#!/usr/bin/env python
#coding=utf-8

import ConfigParser

class readtargets():
    def __init__(self):
        self.cf = ConfigParser.ConfigParser()
        self.cf.read("sqlmanage/targets.conf")

    def workerconf(self):
        directors = self.cf.items('directors')
        managers = self.cf.items('managers')
        dbas = self.cf.items('dbas')[0][1].split(' ')

        devsmap = {}
        drs = []
        mngs = []
        for d in directors:
            drs = drs + d[1].split(' ')
            for m in managers:
                if d[0] == m[0]:
                    mngs = mngs + m[1].split(' ')
                    devsmap[d[1]] = m[1].split(' ')
        return [devsmap, drs, mngs, dbas]

    def dbs(self, dbtype):
        dblist = []
        for db in self.cf.items(dbtype):
            dblist.append(db[0])
        return dblist

