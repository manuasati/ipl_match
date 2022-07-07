from django.contrib import admin
from django.core.exceptions import ValidationError

# Register your models here.
from django.contrib.auth.models import User

from .models import *

# from background_task import background
from .system import *

admin.site.register(Department)

class EnrollAdmin(admin.ModelAdmin):
    list_display = ['email', 'department']
admin.site.register(Enroll, EnrollAdmin)

class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
admin.site.register(Team, TeamAdmin)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'total_points']
admin.site.register(Profile, ProfileAdmin)

class UserGuessAdmin(admin.ModelAdmin):
    list_display = ['user', 'match', 'guess', 'points']
    search_fields = (
        'match__number', "user__email", "points"
    )
    list_filter = ("match", )
admin.site.register(UserGuess, UserGuessAdmin)

class MatchAdmin(admin.ModelAdmin):
    list_display = ['number', 'team1', 'team2', 'scheduled_at', 'status', 'result']
    readonly_fields = ['updated_by']

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user

        if obj.winner:
            if obj.winner.id not in [obj.team1.id, obj.team2.id]:
                raise ValidationError("Team is not belongs to this match. Please go back select correct team")
            obj.result['winner'] = (obj.winner.id)
            obj.save()
            update_users_score(obj.id)

        super().save_model(request, obj, form, change)


admin.site.register(Match, MatchAdmin)

class PredictionAdmin(admin.ModelAdmin):
    list_display = ['title', 'rule', 'guess_range', 'point_weight', 'applied_to', 'rule_explanation', 'is_active']
admin.site.register(Prediction, PredictionAdmin)
