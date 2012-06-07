#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import ConfigParser

import gtk
import gobject

from multiprocessing import Process, Queue

import logging

from pkg_resources import resource_filename

from filomanager.jobs import job
from filomanager.jobs.menuChef import menuChef

#from multiprocessing import Process, Queue


class jobManager:
	def __init__(self, jobName, configFile):

		config = ConfigParser.ConfigParser()
		config.read(configFile)

		self.jobName = jobName
		self.configFile = configFile

		self.q = Queue()

		self.builder = gtk.Builder()
		#runJobGlade=os.path.join( config.get("miscellaneous","glade-dir") , "runjob.glade")
		runJobGlade=resource_filename('filomanager.ui', 'glade/runjob.glade')
		#runJobGlade=os.path.join( config.get("miscellaneous","glade-dir") , "runjob.glade")
		self.builder.add_from_file(runJobGlade)

		parameters = self.builder.get_object("parametersList")
		for param in self.get_jobParameters(jobName):
			parameters.append( [param, None ] )

		self.builder.get_object("jobStatus").hide()

		self.dialog = self.builder.get_object("dialogRunJob")
		self.dialog.connect("show", self._dialogUp)
#		self.dialog.connect('response', self.stop)

		closeButton = self.builder.get_object("start")
		closeButton.connect("clicked", self.start)

		closeButton = self.builder.get_object("Close")
		closeButton.set_sensitive(True)
		closeButton.connect("clicked", self.stop)


		logger=logging.getLogger(jobName)
		if len(logger.handlers) == 0:
			formatter = logging.Formatter( '%(asctime)-6s: %(levelname)s - %(message)s' )
			fileLogger = logging.FileHandler( filename = os.path.join( config.get('Menu-chef','log-dir'), self.jobName+".log") )
			fileLogger.setFormatter( formatter )
			fileLogger.setLevel( logging.INFO )
			logger.setLevel( logging.INFO )
			logger.addHandler( fileLogger )


		self.j = globals()[jobName]( self.configFile, self.q )
		self.dialog.set_title(self.j.name)

		self.update_window()

		self.dialog.show_all()
		self._tag = gobject.timeout_add(1000, self.update_window)

	def get_jobParameters(self, jobName):
		return [ x for x in dir(globals()[jobName]) if x not in dir(job) ]

	def set_jobParameters(self, **kw ):
		parameters = self.builder.get_object("parametersList")
		for param in kw.keys():
			for i in range(parameters.iter_n_children(None)):
				iter=parameters.get_iter(i)
				if parameters.get_value(iter,0)==param:
					parameters.set_value(iter,1,kw[param])
			self.j.set_parameter(param, kw[param])
		self.params=kw

	def start( self, widget=None ):

		try:
			self.j
		except AttributeError:
			self.j = globals()[self.jobName]( self.configFile, self.q )
			self.dialog.set_title(self.j.name)
			gobject.source_remove(self._tag)
			self._tag = gobject.timeout_add(1000, self.update_window)
			for param in self.params.keys():
				self.j.set_parameter(param, self.params[param])

		if self.j.is_alive():
			raise RuntimeError('Unable to start, job is alive')

		self.j.start()

	def stop(self, widget=None):
		self.dialog.hide()

	def getGUI(self):
		return self.dialog

	def get_jobIcon(self):
		return self.builder.get_object("jobIcon")

	def _dialogUp( self, widget ):
		print "dialogUp()"
#		self.lockStart.release()


	def update_window( self ):
		try:
			progressbar=self.builder.get_object("progressJob")
			jobLog=self.builder.get_object("logBuffer")

			while not self.q.empty():
				(text, pbar) = self.q.get()
				iter = jobLog.get_end_iter()
				jobLog.insert( iter, text +"\n" )
				if pbar is not None and pbar >= 0 and pbar <= 100:
					progressbar.set_fraction(pbar/100.0)
					progressbar.set_text(str(pbar)+"%" )
#				self.builder.get_object("jobLog").scroll_to_iter(iter, within_margin=False )
				self.builder.get_object("jobLog").scroll_to_mark(jobLog.get_insert(), within_margin=False )

			if self.j.pid is not None:
				if self.j.is_alive():
					self.dialog.set_title(self.j.name+" [running]")
					self.builder.get_object("jobStatus").set_from_stock(gtk.STOCK_REFRESH, gtk.ICON_SIZE_SMALL_TOOLBAR)
					self.builder.get_object("stop").set_sensitive(True)
					self.builder.get_object("start").set_sensitive(False)
					return True
				elif self.j.exitcode == 0:
					self.builder.get_object("jobStatus").set_from_stock(gtk.STOCK_APPLY, gtk.ICON_SIZE_SMALL_TOOLBAR)
					self.dialog.set_title(self.j.name+" [finished]")
					self.builder.get_object("stop").set_sensitive(False)
					self.builder.get_object("start").set_sensitive(True)
					del self.j
					return False
				else:
					self.builder.get_object("jobStatus").set_from_stock(gtk.STOCK_DIALOG_ERROR, gtk.ICON_SIZE_SMALL_TOOLBAR)
					self.dialog.set_title(self.j.name+" [abort]")
					self.builder.get_object("stop").set_sensitive(False)
					self.builder.get_object("start").set_sensitive(True)
					iter = jobLog.get_end_iter()
					jobLog.insert( iter, "exitcode="+str(self.j.exitcode)+"\n" )
					self.builder.get_object("jobLog").scroll_to_mark(jobLog.get_insert(), within_margin=False )
					del self.j
					return False
			else:
				self.builder.get_object("stop").set_sensitive(False)
				self.builder.get_object("start").set_sensitive(True)
				return True
		except:
			pass



print globals().keys()
#import filomanager.jobs.mailChimp as mailChimp
