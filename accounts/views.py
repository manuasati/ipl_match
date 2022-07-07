from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages

from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User

# Create your views here.
from .models import *
from .forms import CreateUserForm

from django.http import JsonResponse


def enrollPage(request):
    context = {"error": None, "success": None}
    context["departments"] = Department.objects.all()
    if request.method == 'POST':
        dept = None
        email = request.POST.get('email')
        dept_id = request.POST.get('dept_id')
        
        context['email'] = email
        context['dept_id'] = int(dept_id)
        
        if email.split('@')[-1] != "amadeus.com":
            context['error'] = "please enter amadeus email."
            return render(request, 'accounts/enroll.html', context)

        if Enroll.objects.filter(email=email):
            context['email'] = ""
            context['dept_id'] = ""
            context['success'] = "this email is already registered."
            return render(request, 'accounts/enroll.html', context)

        if not dept_id:
            context['error'] = "Please select department."
            return render(request, 'accounts/enroll.html', context)
        if dept_id:
            dept = Department.objects.filter(id=dept_id).first()
            if not dept:
                context['error'] = "Please select department."
                return render(request, 'accounts/enroll.html', context)
        if dept:
            Enroll(email=email, department=dept).save()
            context['email'] = ""
            context['dept_id'] = ""
            context["success"] = "thank you registering...."
    return render(request, 'accounts/enroll.html', context)


def registerPage(request):
    if 'playipl' not in request.path_info:
        return redirect('/playipl/register')

    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user_model = get_user_model()
                username = form.cleaned_data.get('username')
                user = user_model.objects.get(username=username)

                name_text = user.email.split("@")[0].split(".")
                if len(name_text) >= 2:
                    user.first_name = name_text[0].capitalize()
                    user.last_name = name_text[1].capitalize()
                else:
                    user.first_name = name_text[0].capitalize()
                user.save()
                    
                department = form.cleaned_data.get('department')
                department = Department.objects.get(id=department)
                profile = Profile(user=user, department=department)
                profile.save()

                messages.success(request, 'Account was created for ' + user.email)
                
                return redirect('login')
            

        context = {'form':form}
        context["departments"] = Department.objects.all()
        return render(request, 'accounts/register.html', context)

def loginPage(request):
    if 'playipl' not in request.path_info:
        return redirect('/playipl/login')

    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password =request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Username OR password is incorrect')

        context = {}
        return render(request, 'accounts/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')




def home(request):
    if 'playipl' not in request.path_info:
        return redirect('/playipl')


    users = Profile.objects.all().order_by("-total_points")
    matches_played = Match.objects.filter(status='PLAYED').order_by("-scheduled_at")
    matches_fixtures = Match.objects.filter(status='NOT_STARTED').order_by("scheduled_at")
    matches_ongoing = Match.objects.filter(status='ONGOING')

    predictions = Prediction.objects.filter(is_active=True)
    profile = None
    if request.user.is_authenticated:
        profile = Profile.objects.filter(user=request.user).first() 
        if not profile:
            profile = Profile(user=request.user, department=Department.objects.get(id=1))
            profile.save()
            profile = Profile.objects.filter(user=request.user).first()


        for match in matches_played:
            user_guess = UserGuess.objects.filter(match=match, user=request.user).first()
            if user_guess:
                match.user_guess = user_guess.guess
                match.save()

        for match in matches_ongoing:
            user_guess = UserGuess.objects.filter(match=match, user=request.user).first()
            if user_guess:
                match.user_guess = user_guess.guess
                match.save()

        for match in matches_fixtures:
            user_guess = UserGuess.objects.filter(match=match, user=request.user).first()
            if user_guess:
                match.user_guess = user_guess.guess
                match.save()

    context = {
        'matches_played': matches_played,
        'matches_ongoing': matches_ongoing,
        'matches_fixtures': matches_fixtures,
        'predictions': predictions,
        'users': users,
        'profile': profile 
    }
    context["departments"] = Department.objects.all()

    return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='login')
def postGuess(request):
    match_id = request.GET.get('match_id', "").strip()
    if not match_id:
        return JsonResponse({'status': 'error', 'message': 'match-id is missed!'})
    
    match = Match.objects.filter(id=match_id).first()
    if not match:
        return JsonResponse({'status': 'error', 'message': 'wrong match-id!'})

    if match.status not in ["NOT_STARTED"]:
        return JsonResponse({'status': 'error', 'message': 'No guess allowed on played/ongoing match!'})

    winner_team_id = request.GET.get('winner', "").strip()
    if not winner_team_id:
        return JsonResponse({'status': 'error', 'message': 'winner team-id is missed!'})
    
    if int(winner_team_id) not in [match.team1.id, match.team2.id]:
        return JsonResponse({'status': 'error', 'message': 'winner team not belongs to this match!'})

    user_guess, _ = UserGuess.objects.get_or_create(user=request.user, match=match)
    user_guess.guess = {
        "winner": int(winner_team_id),
        "winning_team_score": int(request.GET.get("winning_team_score", 0)),
        "winner_total_sixes": int(request.GET.get("winner_total_sixes", 0)),
        "winner_total_wickets": int(request.GET.get("winner_total_wickets", 0)),
    }
    user_guess.save()
    return JsonResponse({'status': 'success', 'message': 'your guess has been saved!'})


 