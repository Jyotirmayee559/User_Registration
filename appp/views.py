from django.shortcuts import render


# Create your views here
from appp.forms import *
from django.http import HttpResponse,HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.core.cache import cache
from appp.models import *
import random


def registration(request):
    EUFO=UserForm()
    EPFO=ProfileForm()
    d={'EUFO':EUFO,'EPFO':EPFO}

    if request.method=='POST' and request.FILES:
        NMUFDO=UserForm(request.POST)
        NMPFDO=ProfileForm(request.POST,request.FILES)
        if NMUFDO.is_valid() and NMPFDO.is_valid():
            MFUFDO=NMUFDO.save(commit=False)
            pw=NMUFDO.cleaned_data['password']
            MFUFDO.set_password(pw)
            MFUFDO.save()

            MFPFDO=NMPFDO.save(commit=False)
            MFPFDO.username=MFUFDO
            MFPFDO.save()
            send_mail('registartion',
                      'Thank u for registration',
                      'ompravab@gmail.com',
                      [MFUFDO.email],
                      fail_silently=False)

        
        
            return HttpResponse('Registartion is Successfull')
        else:
            return HttpResponse('Not valid')


    return render(request,'registration.html',d)


def home(request):
    if request.session.get('username'):
        username=request.session.get('username')
        d={'username':username}
        return render(request,'home.html',d)
    return render(request,'home.html')


def user_login(request):
    if request.method=='POST':
        username=request.POST['un']
        password=request.POST['pw']
        AUO=authenticate(username=username,password=password)
        if AUO and AUO.is_active:
            login(request,AUO)
            request.session['username']=username
            return HttpResponseRedirect(reverse('home'))
        else:
            return HttpResponse('Invalid Credentials')
    return render(request,'user_login.html')


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))

@login_required
def display(request):
    username=request.session['username']
    UO=User.objects.get(username=username)
    PO=Profile.objects.get(username=UO)
    d={'UO':UO,'PO':PO}
    return render(request,'display.html',d)

@login_required
def change_password(request):
    if request.method=='POST':
        pw=request.POST['cpw']
        username=request.session['username']
        UO=User.objects.get(username=username)
        UO.set_password(pw)
        UO.save()
        return HttpResponse('Password Changed')
    
    return render(request,'change_password.html')

def reset_password(request):
    if request.method=="POST":
        # cpw=request.POST['pw']
        username=request.POST['un']
        cun=request.POST['un']
        LUO=User.objects.filter(username=cun)
        if LUO:
            UO=LUO[0]
            # UO.set_password(cpw)
            # UO.save()
            otp=random.randint(100000,999999)
            cache.set(f'{username}_otp',otp,timeout=300)
            send_mail('Reset Password','Your OTP is'+str(otp),'ompravab@gmail.com',[UO.email],fail_silently=False)
            request.session['username']=username
            return HttpResponseRedirect(reverse('verify_otp'))
        else:
            return HttpResponse('Password is Not Changed')

    return render(request,'reset_password.html')


def verify_otp(request):
    if request.method=="POST":
        otp_entered=request.POST['otp']
        username=request.session.get('username') 
        if not username:
            return HttpResponse('session expired,please try again.')
        #retrievev the OTP from the cache
        otp_stored=cache.get(f'{username}_otp')
        if otp_stored and str(otp_stored)==otp_entered:
            #otp is correct,allow password reset
            return HttpResponseRedirect(reverse('home'))
        else:
            return HttpResponse("Invalid OTP")
    return render(request,'verify_otp.html')