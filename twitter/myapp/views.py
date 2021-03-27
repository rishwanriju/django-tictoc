from django.shortcuts import render,redirect,HttpResponse
from .forms import registerForm,loginForm,updateForm
from django.contrib.auth import login,logout,authenticate,update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .models import tweet,like,comment,friends,custModel,messages as msg,msngr
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


def notLogined(fn):
    def warpper(request):
        if(request.user.is_authenticated):
            return redirect("home")
        else:
            return fn(request)
    return warpper

def handler404(request,a):
    return render(request, 'error404.html', status=404)

def handler500(request):
    return render(request, 'error500.html', status=500)



def paging(query,number=12,page=1):
    paginator = Paginator(query, number)
    try:
        result = paginator.page(page)
    except PageNotAnInteger:
        result = paginator.page(1)
    except EmptyPage:
        result = paginator.page(paginator.num_pages)
    return result


@notLogined
def loginFn(request):
    nxt=request.GET.get('next')
    if not nxt:
        nxt="home"
    if request.method=="POST":
        form=loginForm(request.POST)
        
        if form.is_valid():
            username=form.cleaned_data["email"]
            password=form.cleaned_data["password"]
            user=authenticate(request,username=username,password=password)
            if(user):
                login(request,user)
                return redirect(nxt)
        
        return render(request,"account/login.html",{"form":form})
    else:
        form=loginForm()
        return render(request,"account/login.html",{"form":form})

@notLogined
def registerFn(request):
    if request.method=="POST":
        form=registerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
        else:
            return render(request,"account/register.html",{"form":form})
    else:
        form=registerForm()
        return render(request,"account/register.html",{"form":form})

def logoutFn(request):
    logout(request)
    return redirect("login")

@login_required(login_url="login")
def homeFn(request):
    if request.method=="POST":
        content=request.POST.get("content")
        img=request.FILES.get("img")
        if img:
            if img.name[-4:] not in [".png",".jpg","jpeg"]:
                messages.error(request, 'unspported type media')
                return redirect('home')

        if(content or img):
            form=tweet(content=content,author=request.user,img=img)
            form.save()
        return redirect('home')
        
    n=request.GET.get('page', 1)
    posts=tweet.objects.all().order_by('-id')
    posts=paging(posts,6,n)
    return render(request,"home.html",{"posts":posts})


@login_required(login_url="login")
def post(request,id):
    obj=tweet.objects.get(id=id)
    comments=comment.objects.filter(post=obj)
    return render(request,"post.html",{"post":obj,"comments":comments})

@login_required(login_url="login")
def deletePost(request,id):    
    obj=tweet.objects.get(author=request.user,id=id)
    obj.delete()
    return redirect("home")

@login_required(login_url="login")
def likePost(request,id):
    post=tweet.objects.get(id=id)
    obj=like.objects.filter(user=request.user,post=post)
    if obj:
        obj[0].delete()
    else:
        obj=like(user=request.user,post=post)
        obj.save()
    return HttpResponse("<script>window.location.replace(document.referrer);</script>")


@login_required(login_url="login")
def addComment(request,id):
    post=tweet.objects.get(id=id)
    comments=request.POST["comments"]
    obj=comment(user=request.user,post=post,comments=comments)
    obj.save()
    return redirect("/post/"+str(id)+"/")


@login_required(login_url="login")
def deleteComment(request,pid,cid):
    post=tweet.objects.get(id=pid)
    obj=comment.objects.filter(user=request.user,post=post,id=cid)
    if obj:
        obj[0].delete()
    return HttpResponse("<script>window.location.replace(document.referrer);</script>")


@login_required(login_url="login")
def searchFn(request):
    name=request.GET.get("user")
    persons=custModel.objects.all().filter(username__icontains=name).exclude(username=request.user.username).order_by('-id')
    friend = friends.objects.filter(follower=request.user)
    friend = [ i['friend_id'] for i in friend.values()]
    return render(request,"search.html",{"persons":persons,"friends":friend})


@login_required(login_url="login")    
def followingFN(request,id,userid):
    print("\n\n req",id,userid,"\n")
    if id==userid:
        return HttpResponse("<script>alert('cant follow yourself');window.location.replace(document.referrer);</script>")

    if not userid == request.user.id:
        return HttpResponse("<script>alert('come back after login ');window.location.replace('/login/');</script>")

    friend =custModel.objects.filter(id=id)
    if not friend:
        return HttpResponse("<script>alert('nice try');window.location.replace(document.referrer);</script>")

    objt=friends.objects.filter()
    if objt:
        objt[0].delete()
        return HttpResponse("<script>alert('Unfollowed');window.location.replace(document.referrer);</script>")

    else:
        obj=friends(follower=request.user,friend=friend[0])
        obj.save()
        print(objt)
        return HttpResponse("<script>alert('you followed {}');window.location.replace(document.referrer);</script>".format(friend[0].username))

    

@login_required(login_url="login")    
def mypost(request):
    if request.method=="POST":
        content=request.POST["content"]
        if content!="":
            form=tweet(content=content,author=request.user)
            form.save()
        return redirect('/posts/')

    no=request.GET.get("page",1)
    posts=tweet.objects.filter(author=request.user).order_by('-id')
    posts=paging(posts,6,no)
    return render(request,"home.html",{"posts":posts})

@login_required(login_url="login")    
def settingsFn(request):
    return render(request,"settings.html")

@login_required(login_url="login")    
def updateFn(request):
    if request.method=="POST":
        form=updateForm(request.POST,instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('settings')
        else:
            return render(request,"settings.html",{"form":form})
    else:
        form=updateForm(instance=request.user)
        return render(request,"account/profile_edit.html",{"form":form})

@login_required(login_url="login") 
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('settings')
        else:
            args = {'form': form}
            return render(request, 'account/password_change_form.html', args)
    else:
        form = PasswordChangeForm(user=request.user)
        args = {'form': form}
        return render(request, 'account/password_change_form.html', args)

@login_required(login_url="login")
def deleteAccFn(request):
    username=request.user.username
    print(username,request.user.id)
    logout(request)
    obj=custModel.objects.get(username=username)
    obj.delete()
    return render(request,'deleteacc.html',{'username':username})

@login_required(login_url="login")
def myProfileFn(request,user):
    if user=='account':
        data=request.user
    else:
        data=custModel.objects.get(username=user)
    return render(request,'profile.html',{'data':data})

@login_required(login_url="login")    
def hispost(request,username):
    no=request.GET.get("page",1)
    user=custModel.objects.get(username=username)
    posts=tweet.objects.filter(author=user)
    posts=paging(posts,6,no)
    return render(request,"posts.html",{"posts":posts,"username":username})


@login_required(login_url="login")   
def chat(request,id):
    user1 = custModel.objects.get(id=id)
    user2 = request.user
    obj=msngr.objects.filter(Q(user1=user1,user2=user2) | Q( user1=user2,user2=user1 ))
    print(obj)
    if not obj:
        obj=msngr(user1=user1,user2=user2)
        obj.save()
    else:
        obj=obj[0]
    print(obj)
    return redirect("/msg/"+str(obj.id)+"/")

@login_required(login_url="login")   
def messageList(request):
    user=request.user
    msgs=msngr.objects.filter(Q(user1=user) | Q(user2=user))
    no=request.GET.get("page",1)
    msgs=paging(msgs,6,no)
    return render(request,'inbox.html',{"msgs":msgs})

@login_required(login_url="login")   
def msgDelete(request,id):
    user=request.user
    msgs=msngr.objects.filter(Q(user1=user) | Q(user2=user))
    msgs=msgs.get(id=id)
    msgs.delete()
    return redirect('/inbox/')

@login_required(login_url="login")   
def msgs(request,id):
    user=request.user
    obj=msngr.objects.filter(Q(user1=user) | Q(user2=user),id=id)[0]

    if request.method=="POST":
        txt=request.POST["txt"]
        if(txt !=""):
            ob=msg(msg=txt,sender=request.user,user=obj)
            ob.save()

    chat=msg.objects.filter(user=obj)
    return render(request,'msgs.html',{"msgs":chat})



