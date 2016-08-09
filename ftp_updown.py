#!/usr/bin/env python
# –*– encoding: UTF-8 –*–

'''ftp_updown.py: connection to FTP and up & down function'''

__author__ 		= 'frantisekrehor.cz'
__email__		= 'hi@frantisekrehor.cz'

#=========================================================================
	
#importing necessary modules for running script

import os, errno
import ftplib


#definitions of available methods

def ftp_connect(server, usr, pswd):
	''' Creater connection object and login to FTP server '''
	
	try:
		conn = ftplib.FTP(server)
		conn.login(user = usr, passwd = pswd)
	
	except IOError as (errno, strerror):
		print "I/O error(%r): %r" % (errno, strerror)
		return False
	
	print 'Successfully connected to "%s"' % server
	return conn
		
	
def ftp_up(connection, path, data, file_output = None):
	''' Uploading a file to FTP '''
	
	# file_output
	if not file_output:
		file_output = os.path.basename(os.path.realpath(data))
	
	try:
		# changing FTP working directory
		connection.cwd(path)
		# open the file and upload
		with open(file_output, 'rb') as out:
			connection.storbinary('STOR ' + file_output, out)
	
	except IOError as (errno, strerror):
		print "I/O error(%r): %r" % (errno, strerror)
		return False
    
	print 'File "%s" successfully uploaded to "%s"' % (file_output, path)
	return True
	
	
def ftp_down(connection, path, data, file_output = None):
	''' Downloading a file from FTP '''
	
	# file_output
	if not file_output:
		file_output = os.path.basename(os.path.realpath(data))
	
	try:
		# changing FTP working directory
		connection.cwd(path)
		# open the file for writing and write data from FTP
		with open(file_output, 'wb') as out:
			connection.retrbinary('RETR ' + data, out.write)
	
	except IOError as (errno, strerror):
		print "I/O error(%r): %r" % (errno, strerror)
		return False
    
	print 'File "%s" successfully downloaded from "%s"' % (file_output, path)
	return True



