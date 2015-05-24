# -*- coding: utf8 -*-


import sys
from jinja2 import Template
import sqlite3


def export_layout(db, html_writer):
    sql = """
    SELECT
        market_penetration.country_name,
        nb_internauts,
        nb_sales,
        market_penetration.penetration_rate,
        penetration_performance.norm_spread > 2 AS over_performing,
        penetration_performance.norm_spread < -2 AS under_performing
    FROM
        market_penetration
    JOIN penetration_performance
            ON market_penetration.country_code = penetration_performance.country_code
    """
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    cur.execute(sql)
    countries = cur.fetchall()
    tpl_filename = "perf.tpl.html"
    with open(tpl_filename, "r") as f_tpl:
        t = Template(f_tpl.read())
    html_writer.write(t.render(countries = countries))


def main():
    with sqlite3.connect("stats.sqlite") as db, \
         open("penetration_rate.html", "w") as html_writer:
        export_layout(db, html_writer)
    return 0

if __name__ == '__main__':
    sys.exit(main())