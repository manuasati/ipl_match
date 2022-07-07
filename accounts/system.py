from .models import *
from django.db.models import Sum

# from background_task import background


def get_range_point(actual_result, prediction, range):
    lower = 0 if (actual_result - range) <=0 else actual_result - range
    upper = actual_result + range

    if lower <= prediction <= upper:
        point = (range - abs(prediction- actual_result))
        return point
    return 0


# @background(schedule=3)
def update_users_score(match_id):
    match = Match.objects.get(id=match_id)

    user_guesses = UserGuess.objects.filter(match=match)
    for ug in user_guesses:
        total_match_points = 0
        for guess_field, guess_value in ug.guess.items():
            prediction = Prediction.objects.get(filed_to_refer=guess_field)
            match_result = match.result.get(guess_field)
            
            if prediction.rule == 0: #exact match
                if guess_value == match_result:
                    total_match_points += prediction.point_weight

            elif prediction.rule == 1: #range
                points = get_range_point(actual_result=match_result, prediction=guess_value, range=prediction.guess_range)
                total_match_points += points * prediction.point_weight
        
        ug.points = total_match_points
        ug.save()

    for profile in Profile.objects.all():
        us = UserGuess.objects.filter(user=profile.user).aggregate(total_points=Sum('points'))
        profile.total_points = us.get('total_points', 0)
        profile.save()

