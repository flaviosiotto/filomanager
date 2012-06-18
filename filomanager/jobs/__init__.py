#!/usr/bin/env python
# -*- coding: utf-8 -*-

print "__init__.py"

import datetime

import ConfigParser

import logging

import sys

from multiprocessing import Process, Queue

class job(Process):

	def __init__(self, configFile, q, **kw):
		self.q = q
		super(job, self).__init__(name=self.__class__.__name__)

		self.__dict__.update(kw)
		self.__dict__.update(locals())

		config = ConfigParser.ConfigParser()
		config.read(configFile)

		self.env = dict()
		for section in config.sections():
			self.env[section]=dict()
			for opt in config.options(section):
				self.env[section][opt] = config.get(section, opt)

		self.requestStop=False

		self.logger=logging.getLogger(self.name)

	def set_parameter( self, paramName, paramValue ):
		self.__dict__[paramName]=paramValue

	def logInfo(self, level, text, pbar=None):
		print str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+": "+ text

		if level == logging.INFO:
			self.logger.info(text)
		elif level == logging.WARNING:
			self.logger.warning(text)
		elif level == logging.ERROR:
			self.logger.error(text)

		self.q.put( (str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+": "+text, pbar) )

	def runJob(self):
		pass


	def run(self):
		try:
			self.logInfo(logging.INFO, "job "+self.name+" started", 0)
			self.logInfo(logging.INFO, "env: "+str(self.env), 0)

			self.runJob()

			self.logInfo(logging.INFO, "job "+self.name+" finished", 100)

		except:
			self.logInfo(logging.ERROR, str(sys.exc_info()[1]) )
			self.logInfo(logging.INFO, "job "+self.name+" finished")
			raise
		finally:
			pass
