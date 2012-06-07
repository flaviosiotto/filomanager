#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lpod.document import odf_new_document

from filomanager.jobs import job

from filomanager.stages import postgresql
from filomanager.stages import gtranslate

from pkg_resources import resource_filename

import os

import logging

class menuChef(job):
	translate=None
	today=None

	def runJob(self):
		if not self.requestStop:
			
			document = odf_new_document( resource_filename(__name__, "templates/menu-chef.ott" ) )
			body = document.get_body()
			t_starters = body.get_table(name=self.env["Menu-chef"]["starters-list-name"])
			r_starters = t_starters.get_row(0).clone()
			t_firsts = body.get_table(name=self.env["Menu-chef"]["first-courses-list-name"])
			r_firsts = t_firsts.get_row(0).clone()
			t_seconds = body.get_table(name=self.env["Menu-chef"]["second-courses-list-name"])
			r_seconds = t_seconds.get_row(0).clone()

		if not self.requestStop:
			self.logInfo(logging.INFO, "extract data from quickOrder", 20)

			res=postgresql.extractChefMenu( host=self.env["QuickOrder DB"]["host"], 
									dbName=self.env["QuickOrder DB"]["dbname"],
									User=self.env["QuickOrder DB"]["user"],
									Pass=self.env["QuickOrder DB"]["password"] )

			i_starters, i_firsts, i_seconds = 0, 0, 0
			for row in res:
				if row['category']=='antipasto':
					r = r_starters
					t = t_starters
					i = i_starters
					i_starters += 1
				elif row['category']=='primo':
					r = r_firsts
					t = t_firsts
					i = i_firsts
					i_firsts += 1
				elif row['category']=='secondo':
					r = r_seconds
					t = t_seconds
					i = i_seconds
					i_seconds += 1

				descCell = r.get_cell( 0 )
				if self.translate is None:
					text = row['description']
				else:
					text = gtranslate.translate(row['description'], src='it', to=self.translate)
				descCell.set_value( text.decode('utf-8') )
				priceCell = r.get_cell( 1 )
				priceCell.set_value( row['price'] )
				r.set_cell(0, descCell)
				r.set_cell(1, priceCell)
				t.insert_row(i, r)
#				print row['category'] + " " + row['description'] + " " + str(row['price'])

		if not self.requestStop:
			if self.translate is None:
				lang="it" 
			else:
				lang=self.translate
			outputFileName = self.env["Menu-chef"]["file-output-dir"]+"/"+\
								self.today.strftime("%d-%m-%Y")+"-"+\
								lang + "_" + self.env["Menu-chef"]["file-output-name"]+"."+\
								self.env["Menu-chef"]["file-output-format"]
			document.save( outputFileName )
			self.logInfo(logging.INFO, "open document "+outputFileName, 75)
			os.system("oowriter "+outputFileName)


