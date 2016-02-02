# -*- coding: utf-8 -*-
from django.db import models

class Galaxy(models.Model):
	obj_id = models.BigIntegerField()
	ra = models.FloatField()
	dec = models.FloatField()
	
	def __unicode__(self):
		return u":".join([str(self.obj_id), str(self.ra), str(self.dec)])		

class Pair(models.Model):
	obj_one = models.ForeignKey(Galaxy, related_name='obj_one')
	obj_two = models.ForeignKey(Galaxy, related_name='obj_two')
	distance = models.FloatField()
	
	def __unicode__(self):
		return u":".join([str(self.obj_one.obj_id), str(self.obj_two.obj_id), str(self.distance)])