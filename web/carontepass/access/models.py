# -*- encoding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
import datetime
from telegram_group import send_group_msg, send_simple_msg, send_log_msg


# Create your models here.

class Device(models.Model):
    __tablename__ = 'cp_device'
    
    NFC = 'nfc'
    MAC = 'mac'
    TAG = 'tag'
    DEVICE_CHOICES = (
        (NFC, 'NFC'),
        (MAC, 'MAC'),
        (TAG, 'TAG'),
    )

    user = models.ForeignKey(User)
    kind = models.CharField(max_length=3,
                                      choices=DEVICE_CHOICES,
                                      default=NFC,
                                      blank=False,
                                      )
    code = models.CharField(max_length=64, blank=False)
    
    def __str__(self):
        return 'Device {}:{} - {}'.format(self.user, self.kind, self.code)
        
    @staticmethod   
    def check_exists_device(code_id):
        #If there is no device code creates a new one.
        #With this you have saved the new devices and then assign them to your user.
        
        if not Device.objects.filter(code=code_id):
            caronte = User.objects.filter(username="caronte").first()
            device_create = Device.objects.create(user=caronte, kind='tag', code=code_id)


class Log(models.Model):
    __tablename__ = 'cp_log'

    user = models.ForeignKey(User)
    ts_input = models.DateTimeField()
    ts_output = models.DateTimeField()
    user_in = models.BooleanField(default=False)
    
    def __str__(self):
        return 'Log {}: {} - {}'.format(self.user, self.ts_input, self.ts_output)
    
    @staticmethod   
    def checkentryLog(Device):

        date = datetime.datetime.now()

        log_obj = Log.objects.filter(user=Device.user).last()
        
        log_user_in_initial = len(Log.objects.filter(user_in=True).all())

        if not log_obj:

            log_create = Log.objects.create(user=Device.user, ts_input=date, ts_output=date, user_in=True)
            send_log_msg(True, str(Device.user.username))
            
            
        elif(log_obj.user_in == True):
                    
            log_obj.ts_output = datetime.datetime.now()
            log_obj.user_in = False
            log_obj.save()
            send_log_msg(False, str(Device.user.username))
            

        else:
            log_create = Log.objects.create(user=Device.user, ts_input=date, ts_output=date, user_in=True)    
            send_log_msg(True, str(Device.user.username))
            
     
        log_user_in_end = len(Log.objects.filter(user_in=True).all())
        
        
        if(log_user_in_initial == 0 and log_user_in_end == 1):
            send_group_msg(True, str(Device.user.username))

        elif(log_user_in_initial == 1 and log_user_in_end == 0):
            send_group_msg(False, str(Device.user.username))
           
            
    @staticmethod   
    def listUsersInside():
        
        users = Log.objects.filter(user_in=True).all()
        
        if users:
            users_in_msg = 'People registered here are: {}'.format(
    	  	', '.join([str(users[i].user.username) for i in range(len(users))])
    	 	 )
    	else:
    	     users_in_msg = 'Nobody inside'
                
        
        return users_in_msg


    @staticmethod    
    def listUsersCount():

        return Log.objects.filter(user_in=True).count()
            

class Message(models.Model):
    __tablename__ = 'cp_message'
    
    INPUT = 'Input'
    OUTPUT = 'Output'
    CAUTION = 'Caution'
    INFO = 'Info'
    
    ROL_CHOICES = (
        (INPUT, 'Input'),
        (OUTPUT, 'Output'),
        (CAUTION, 'Caution'),
        (INFO, 'Info'),
    )
    
    text = models.CharField(max_length=512)
    
    rol = models.CharField(max_length=7,
                                      choices=ROL_CHOICES,
                                      default=INFO,
                                      blank=False,
                                      )
                                    
    @staticmethod 
    def message_detect_tag(Device):

        #If the user has assigned chatid sends message to the telegram
        if Telegram.objects.filter(user=Device.user).count() > 0:
            
            chatid = Telegram.objects.filter(user=Device.user).first().chatid
        
            if Log.objects.filter(user=Device.user, user_in=True).last():
                #welcome message, select random message
                text = Message.objects.filter(rol="Input").order_by('?').first().text
                text += ", " + Device.user.first_name + "."
                
            else:
                #goodbye message, select random message
                text = Message.objects.filter(rol="Output").order_by('?').first().text
                text += ", " + Device.user.first_name + "."
                
                
            send_simple_msg(chatid, text)  
    
    
    def __str__(self):
        return '{}: {}'.format(self.rol, self.text)
    


class Payment(models.Model):
    __tablename__ = 'cp_payment'

    year = models.IntegerField()
    month = models.IntegerField()
    user = models.ForeignKey(User)
    f_payment = models.DateTimeField()
    amount = models.FloatField(default=0.0)
    
    def __str__(self):
        return '{}: {} - {}'.format(self.user, self.amount, self.f_payment)
 
        
class Telegram(models.Model):
    __tablename__ = 'cp_telegram'
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    chatid = models.DecimalField(max_digits=12, decimal_places=0)
    
    def __str__(self):
        return 'Telegram {}: {}'.format(self.user, self.chatid)
    
    
class SecurityNode(models.Model):
    __tablename__ = 'cp_securitynode'

    DOOR = 'Door'
    TOOL = 'Tool'
    NODE_CHOICES = (
        (DOOR, 'DOOR'),
        (TOOL, 'TOOL'),
    )
    name = models.CharField(max_length=50)
    kind = models.CharField(max_length=4,
                                      choices=NODE_CHOICES,
                                      default=DOOR,
                                      blank=False,
                                      )
    logging = models.BooleanField(default=True)
    telegram = models.BooleanField(default=True)

    def __str__(self):
        return '{} ID: {} '.format(self.name, self.id)

class Acl(models.Model):
    user = models.OneToOneField(User)
    AllowedNodes = models.ManyToManyField(SecurityNode)