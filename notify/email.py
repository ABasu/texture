# -*- coding: utf-8 -*- 

import smtplib, logging, string

################################################################################
class Email(object):
	"""
	A class to send an email once a process has terminated. Useful for 
	remote server processes that take a long time to finish.
	"""
	def __init__(self, from_address, login, pwd, server = 'smtp.gmail.com', port = 587):
		self.from_address = from_address
		self.login = login
		self.pwd = pwd
		self.server = server
		self.port = port


	def send(self, to_addresses, subject, message):
		"""
		Send the email.
		"""
		if isinstance(to_addresses, str):
			to_addresses = [to_addresses]

		msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (self.from_address, ", ".join(to_addresses), subject) )
		msg += "%s\r\n" % message

		server = smtplib.SMTP(self.server, self.port)
		server.set_debuglevel(1)
		server.ehlo()
		server.starttls()
		server.login(self.login, self.pwd)
		server.sendmail(self.from_address, to_addresses, msg)
		server.quit()

