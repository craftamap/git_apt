#!/usr/bin/env python
# encoding: utf-8
import sys
import argparse

import apt
import apt.debfile

import sqlite3

import packaging

import requests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("toll", choices=["update", "download", "upgrade", "add"], nargs=argparse.REMAINDER)
    args = parser.parse_args(sys.argv[1:])
    #print(args)

class databaseHandler():

    def __init__(self):
        self.connect()

    def connect(self):
        """Connects to the db.

        Connects to the db, and saves the connection in self.conn. Also creates
        an cursor self.curs.

        """
        self.conn = sqlite3.connect("git_apt.db")
        self.curs = self.conn.cursor()

    def repositories_get_row_by_value_in_column(self, column, value):
        """gets whole row, where value is in column

        I did this class before I realised I don't know it. Why do I leave it
        in? I don't know
        """
        a = self.curs.execute(("SELECT * FROM repositories WHERE"
                               " {}= :v").format("\"" + column + "\""),
                              {"v": value})
        return a.fetchall()

    def repositories_update_version_git(self, pkg, version):
        """ updates the git version.

        Updates the git version of given package and commits the change
        to the db.
        """
        a = self.curs.execute(("UPDATE repositories SET \"version-git\" = :v "
                              "WHERE pkgname = :p"), {"v": version, "p": pkg})
        self.commit()

    def repositories_update_version_cache(self, pkg, version):
        """ updates the cache version.

        Updates the cache version of the given package and commits the change
        to the db

        """
        a = self.curs.execute(("UPDATE repositories SET \"version-cache\" = :v"
                              " WHERE pkgname = :p"), {"v": version, "p": pkg})
        self.commit()

    def repositories_update_date(self, pkg, date):
        """ updates the date

        Updates the date of the given package and commits the change to the db

        """
        a = self.curs.execute(("UPDATE repositories SET \"date\" = :v"
                              " WHERE pkgname = :p"), {"v": version, "p": pkg})
        self.commit()

    def commit_and_close(self):
        """ commits and closes

        Commits all remaining changes and closes the connection to the db.

        """
        self.commit()
        self.close()



    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


class git_apt():
    pass


if __name__ == '__main__':
    status = main()
    sys.exit(status)
