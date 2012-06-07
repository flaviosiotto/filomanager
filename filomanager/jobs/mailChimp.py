#!/usr/bin/env python
# -*- coding: utf-8 -*-

from filomanager.stages import postgresql

from filomanager.jobs import job

import logging

class sendMail(job):
	today=None
	test=None

	def runJob(self):
		self.logInfo(logging.INFO, "extract data from quickOrder", 20)

#		time.sleep(3)

		res=postgresql.extractChefMenu( host=self.env["QuickOrder DB"]["host"], 
								dbName=self.env["QuickOrder DB"]["dbname"],
								User=self.env["QuickOrder DB"]["user"],
								Pass=self.env["QuickOrder DB"]["password"] )

		startersContent, firstsContent, secondsContent = "", "", ""
		for row in res:
			if row['category']=='antipasto':
				startersContent+=row['description']+' '+str(row['price'])+'<br>'
			elif row['category']=='primo':
				firstsContent+=row['description']+' '+str(row['price'])+'<br>'
			elif row['category']=='secondo':
				secondsContent+=row['description']+' '+str(row['price'])+'<br>'

		self.logInfo(logging.INFO, "build mail content", 30)

		ms = MailSnake( self.env["mailChimp"]['apikey'] )

		menuContent='<h3>Antipasti</h3>'+startersContent+'<h3>Primi</h3>'+firstsContent+'<h3>Secondi</h3>'+secondsContent

		self.logInfo(logging.INFO, "duplicate mail", 40)
		campaignsResult = ms.call('campaigns', params = {'filters': { 'title': 'MenuChef '+ self.today.strftime("%d-%m-%Y"), 'type': 'regular', 'status': 'save' } } )
		if campaignsResult['total'] == 1:
			cid = campaignsResult['data'][0]['id']
			ms.call('campaignUpdate', params = {'cid': cid, 'name': 'content', 'value': { 'html_std_content00': menuContent } } )
		elif campaignsResult['total'] == 0:
			cid = ms.call('campaignReplicate', params = { 'cid': '0a66ed0baa' } )
			if ms.call('campaignUpdate', params = {'cid': cid, 'name': 'title', 'value': 'MenuChef '+ self.today.strftime("%d-%m-%Y") } ):
				ms.call('campaignUpdate', params = {'cid': cid, 'name': 'content', 'value': { 'html_std_content00': menuContent } } )

		if self.test is True:
			self.logInfo(logging.INFO, "send test mail to "+self.env["mailChimp"]["mailstest"], 80)
			ms.call('campaignSendTest', params = {'cid': cid, 'test_emails': [ self.env["mailChimp"]["mailstest"] ] } )
		else: 
			self.logInfo(logging.INFO, "send mail", 80)
			ms.call('campaignSendTest', params = {'cid': cid, 'test_emails': [ self.env["mailChimp"]["mailstest"] ] } )
