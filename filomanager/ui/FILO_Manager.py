#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import datetime
import ConfigParser

import gobject
import pygtk
pygtk.require('2.0')
import gtk

from filomanager.jobs import jobs

from pkg_resources import resource_filename

__author__ = "Flavio Siotto"
__version__ = "0.4"
__email__ = "flavio.siotto@gmail.com"
__status__ = "Development"

#import filomanager.jobs.menuChef as menuChef
#import filomanager.jobs.mailChimp as mailChimp


def getSplits(text,splitLength=4500):
	'''
	Translate Api has a limit on length of text(4500 characters) that can be translated at once, 
	'''
	return (text[index:index+splitLength] for index in xrange(0,len(text),splitLength))


class FILO_Manager:

	def __init__(self, configFile=None ):

		configFile = '/etc/FiloManager.conf'
		self.configFile = configFile

		self.config = ConfigParser.ConfigParser()
		self.config.read( configFile )


		self.builder = gtk.Builder()
		filoGlade=resource_filename(__name__, 'glade/FILO_Manager.glade')
		self.builder.add_from_file( filoGlade )
#		self.builder.add_from_string(pkgutil.get_data(__name__, 'glade/FILO_Manager.glade'))


		today = datetime.date.today()

		dbConn = dict()
		dbConn["host"] = self.config.get("QuickOrder DB", "host")
		dbConn["dbname"] = self.config.get("QuickOrder DB", "dbname")
		dbConn["user"] = self.config.get("QuickOrder DB", "user")
		dbConn["password"] = self.config.get("QuickOrder DB", "password")

		ChefOpt = dict()
		ChefOpt["templates-dir"] = self.config.get("Menu-chef", "templates-dir")
		ChefOpt["starters-list-name"] = self.config.get("Menu-chef", "starters-list-name")
		ChefOpt["first-courses-list-name"] = self.config.get("Menu-chef", "first-courses-list-name")
		ChefOpt["second-courses-list-name"] = self.config.get("Menu-chef", "second-courses-list-name")
		ChefOpt["file-output-dir"] = self.config.get("Menu-chef", "file-output-dir")
		ChefOpt["file-output-format"] = self.config.get("Menu-chef", "file-output-format")
		ChefOpt["file-output-name"] = self.config.get("Menu-chef", "file-output-name")

		options = {"data": today, "QuickOrder-DB": dbConn, "chef-Opt": ChefOpt}


		self.window = self.builder.get_object("FiloManager")
		self.window.set_title("Il Filo - Manager "+__version__)
		self.window.set_icon_from_file( resource_filename(__name__, 'images/FILO_icon.png') )

		self.window.connect("delete_event", self.delete_event)

		self.window.connect("destroy", self.destroy)


		logoImg = self.builder.get_object("logo")
		logoImg.set_from_file( resource_filename(__name__, 'images/logo.png') )	

		companyName = self.builder.get_object("companyName")
		companyName.set_text( self.config.get("company", "name") )

		companyBuffer = self.builder.get_object("companyBuffer")
		companyBuffer.insert_at_cursor( self.config.get("company", "address") + "\n" )
		companyBuffer.insert_at_cursor( self.config.get("company", "city") + " " )
		companyBuffer.insert_at_cursor( self.config.get("company", "country") + "\n" )
		companyBuffer.insert_at_cursor( self.config.get("company", "email") )

		# Creates Buttons 
		IT_Button_menu = self.builder.get_object("chefMenu_IT")
		IT_Image_menu = gtk.Image()
		IT_Image_menu.set_from_file( resource_filename(__name__, 'images/IT_chef.png') )
		
		IT_Button_menu.add(IT_Image_menu)
		IT_Button_menu.connect( "clicked", self.menuChef, { "conv": None, "options": options } )

		EN_Button_menu = self.builder.get_object("chefMenu_EN")
		EN_Image_menu = gtk.Image()
		EN_Image_menu.set_from_file( resource_filename(__name__, 'images/EN_chef.png') )
		EN_Button_menu.add(EN_Image_menu)
		EN_Button_menu.connect( "clicked", self.menuChef, { "conv": "en", "options": options } )

		FR_Button_menu = self.builder.get_object("chefMenu_FR")
		FR_Image_menu = gtk.Image()
		FR_Image_menu.set_from_file( resource_filename(__name__, 'images/FR_chef.png') )
		FR_Button_menu.add(FR_Image_menu)
		FR_Button_menu.connect( "clicked", self.menuChef, { "conv": "fr", "options": options } )

		ES_Button_menu = self.builder.get_object("chefMenu_ES")
		ES_Image_menu = gtk.Image()
		ES_Image_menu.set_from_file( resource_filename(__name__, 'images/ES_chef.png') )
		ES_Button_menu.add(ES_Image_menu)
		ES_Button_menu.connect( "clicked", self.menuChef, { "conv": "es", "options": options } )

		NL_Button_menu = self.builder.get_object("chefMenu_NL")
		NL_Image_menu = gtk.Image()
		NL_Image_menu.set_from_file( resource_filename(__name__, 'images/NL_chef.png') )
		NL_Button_menu.add(NL_Image_menu)
		NL_Button_menu.connect("clicked", self.menuChef, { "conv": "nl", "options": options } )

		Button_mails = self.builder.get_object("Mails")
		Image_mails = gtk.Image()
		Image_mails.set_from_file( resource_filename(__name__, 'images/chefMails.png') )
		Button_mails.add(Image_mails)
		Button_mails.connect("clicked", self.sendMail, { "test": True, "options": options } )

		self.window.show_all()

		gobject.timeout_add(1000, self.update_stats)


	def menuChef( self, widget, data=None ):

		m = jobs.jobManager("menuChef", self.configFile)

		m.set_jobParameters( today=data["options"]["data"], translate=data["conv"] )

		dialog=m.getGUI()
		dialog.set_transient_for(self.window)

		icon = m.get_jobIcon()
		icon.set_from_pixbuf(widget.get_children()[0].get_pixbuf())


	def sendMail( self, widget, data=None ):

		m = jobs.jobManager("sendMail", self.configFile)

		m.set_jobParameters( today=data["options"]["data"], test=data["test"] )

		dialog=m.getGUI()
		dialog.set_transient_for(self.window)

		icon = m.get_jobIcon()
		icon.set_from_pixbuf(widget.get_children()[0].get_pixbuf())


	def update_stats( self ):
#		apiKey = self.config.get("mailChimp", "apiKey")
#		ms = MailSnake(apiKey)
#		accountDetails=ms.call('getAccountDetails',params = {})
#		self.builder.get_object("mailsAvaible").set_text(str(accountDetails['emails_left']))
		self.builder.get_object("data").set_text( datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
		return True
		

	def delete_event(self, widget, event, data=None):
		print "delete event occurred"
		return False

	def destroy(self, widget, data=None):
		print "destroy signal occurred"
		gtk.main_quit()

	def main(self):
		if not os.path.exists( os.path.join( os.environ['HOME'], '.filomanager') ):
			os.makedirs( os.path.join( os.environ['HOME'], '.filomanager') )

		if not os.path.exists( os.path.join( os.environ['HOME'], '.filomanager/log') ):
			os.makedirs( os.path.join( os.environ['HOME'], '.filomanager/log') )

		if not os.path.exists( os.path.join( os.environ['HOME'], '.filomanager/templates') ):
			os.makedirs( os.path.join( os.environ['HOME'], '.filomanager/templates') )

		if not os.path.exists( os.path.join( os.environ['HOME'], '.filomanager/Menuchef') ):
			os.makedirs( os.path.join( os.environ['HOME'], '.filomanager/Menuchef') )

		gtk.main()

