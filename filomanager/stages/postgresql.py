#!/usr/bin/env python
# -*- coding: utf-8 -*-


import psycopg2
import psycopg2.extras

def extractChefMenu( host, dbName, User, Pass ):
#	'''
	conn = psycopg2.connect("host="+host+" "
								"dbname="+dbName+" "
								"user="+User+" "
								"password="+Pass)
	cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cursor.execute("select case when m.Name = 'CHEF ANTIPASTI' \
						then 'antipasto' else \
							case when m.Name = 'CHEF PRIMI' then 'primo' else \
								case when m.Name = 'CHEF SECONDI' then 'secondo' end \
							 end end as category, \
					p.Name as description, p.Price as price \
					from cookbook p, recipe_types m \
					where \
					(m.Name = 'CHEF ANTIPASTI' or m.Name = 'CHEF PRIMI' or m.Name = 'CHEF SECONDI') and p.IDType=m.ID order by m.Name, p.Price;")
	rows=cursor.fetchall()
	conn.close()
#	'''
#	rows=[{"category": "primo", "description": "penne al granchio", "price": 7}]
	for row in rows:
			yield { 'category': row['category'], 'description': row['description'], 'price': row['price'] }
