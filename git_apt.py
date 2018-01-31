#!/usr/bin/env python
# encoding: utf-8
import sys
import argparse

import apt
import apt.debfile

import sqlite3

import re

import packaging.version

import requests

import config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', required=False, action='store_true')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u', "--update", nargs='*')
    group.add_argument('-g', "--upgrade", nargs='*')
    group.add_argument('-d', "--download", nargs='*')
    group.add_argument('-a', "--add", nargs='*')
    # parser.add_argument("toll", choices=["update", "download",
    #                                      "upgrade", "add"],
    #                     nargs=argparse.REMAINDER)
    args = parser.parse_args()
    print(vars(args))


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

    def repositories_get_selected_by_value_in_column(self, selected,
                                                     column, value):
        """gets selected column where value is in column

        I did this class before I realised I don't know it. Why do I leave it
        in? I don't know

        Params:
            Selected
            column
            value
        """
        string = ','.join(map(str, selected))
        a = self.curs.execute(("SELECT {} FROM repositories WHERE"
                               " {}= :v").format(string, "\"" + column + "\""),
                              {"v": value})
        return a.fetchall()

    def full_repositories_get_selected(self, selected):
        """
        is this the real life? or is it fantasy?
        Seriously, anyone who has to maintain this code should kill himself.
        """
        string = ','.join(map(str, selected))
        a = self.curs.execute("SELECT {} FROM repositories".format(string))
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


class git_apt_utilities():

    @staticmethod
    def get_filename_from_cd(cd):
        if not cd:
            return None
        fname = re.findall('filename=(.+)', cd)
        if len(fname) == 0:
            return None
        return fname[0]


class aptHandler():

    def __init__(self):
        self.cache = apt.cache.Cache()

    def _get_package(self, pkg):
        return self.cache[pkg]

    def get_package_version(self, pkg):
        p = self._get_package(pkg)
        return packaging.version.Version(p.installed.version)


class git_api():
    def __init__(self, db):
        self.token = config.git_token
        self.headers = {}
        self.headers["Authorization"] = "token {}".format(self.token)
        self.db = db
        self.baseurl = "https://api.github.com/"
        self.response_storage = {}

    def _get_latest_release(self, git_url):
        if not (git_url in self.response_storage.keys()):
            response = requests.get(self.baseurl + "repos/" + git_url +
                                    "/releases/latest", headers=self.headers)
            self.response_storage[git_url] = response
        else:
            pass
        return self.response_storage[git_url]

    def get_latest_release_version(self, git_url):
        res = self._get_latest_release(git_url)
        ver = res.json()["tag_name"]
        vers = packaging.version.Version(ver)
        return vers

    def get_latest_release_download(self, git_url):
        res = self._get_latest_release(git_url)
        resj = res.json()
        downloadasset = [x for x in resj["assets"] if ".deb" in x["name"]][0]
        return downloadasset["browser_download_url"]

    @staticmethod
    def download_file(url, dest=None, filename=None):
        r = requests.get(url, allow_redirects=True)
        if filename is None:
            filename = git_apt_utilities.get_filename_from_cd(
                r.headers.get('content-disposition')
            )
        if dest is None:
            dest = "downloads"
        open(dest + "/" + filename, 'wb').write(r.content)


class git_apt ():
    def __init__(self):
        self.db = databaseHandler()
        self.git = git_api(self.db)

    def update(self):
        b = self._dblist()
        self._check_git(b)

    def _check_git(self, list1):
        pass
        for k in list1:
            k["version-git"] = self.git.get_latest_release_version(
                k["git-url"]
            )
        print list1

    def _dblist(self):
        requestlist = ["pkgname", "version-git", "version-cache",
                       "git-url", "date"]
        x = self.db.full_repositories_get_selected(
            ["\"" + n + "\"" for n in requestlist]
        )
        return [dict(zip(requestlist, n)) for n in x]


if __name__ == '__main__':
    status = main()
    sys.exit(status)
