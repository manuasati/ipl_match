from django.db import models
from django.contrib.auth.models import User

import jsonfield

class Department(models.Model):
    name = models.CharField(max_length=20)
    def __str__(self):
        return self.name

class Enroll(models.Model):
    email = models.CharField(max_length=200, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="enroll")
    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="profile")
    total_points = models.IntegerField(default=0, null=True)
 

    def __str__(self):
        return self.user.email


class Team(models.Model):
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=200, default="IPL", unique=True)
    
    def __str__(self):
        return self.name

MATCH_EXTRA_FIELDS_DICT = {
    "winner": "Match Winner",
    "winning_team_score": "Winning Team Score",
    "winner_total_sixes": "Winner Total Sixes",
    "winner_total_wickets": "Winning Team Wickets",
}
MATCH_EXTRA_FIELDS = [ (key, value) for key, value in MATCH_EXTRA_FIELDS_DICT.items()]

class Match(models.Model):
    MATCH_EXTRA_FIELDS_DICT_DEFAULT = {k:0 for k, v in MATCH_EXTRA_FIELDS_DICT.items()}
    ALL_STATUS = (
        ('ONGOING', "On going"),
        ('PLAYED', "Played"),
        ('NOT_STARTED', "Not Started"),
        ('ABORTED', "Aborted"),
    )
    number = models.IntegerField(blank=False, unique=True)
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="match_team1")
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="match_team2")
    # cbz_id = models.CharField(max_length=8)
    scheduled_at = models.DateTimeField()
    status = models.CharField(
        max_length=100, choices=ALL_STATUS, default='NOT_STARTED',
    )
    winner = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="match", blank=True, null=True)
    

    result = jsonfield.JSONField(default=MATCH_EXTRA_FIELDS_DICT_DEFAULT)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="match_status", null=True, blank=True)
    

    class Meta:
        unique_together = ('team1', 'team2',)

    def __str__(self):
        return self.team1.code + " Vs " + self.team2.code + " | @" + str(self.scheduled_at)

MATCH = "Match"
LEAGUE = "League"
CATEGORY_LIST = (
    (0, MATCH),
    (1, LEAGUE)
)

RULES = (
    (0, "Exact Match"),
    (1, "Range")
)

class Prediction(models.Model):
    APPLIED_TO = (
        (0, "Number"),
        (1, "Team"),
    )
    filed_to_refer = models.CharField(
        max_length=100, choices=MATCH_EXTRA_FIELDS, blank=False, unique=True,
    )
    title = models.CharField(max_length=300)
    rule_explanation = models.CharField(max_length=300, blank=True, null=True)
    category = models.IntegerField(choices=CATEGORY_LIST, default=0)
    rule = models.IntegerField(choices=RULES, default=0)
    guess_range = models.IntegerField(default=0)
    point_weight = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    applied_to = models.IntegerField(choices=APPLIED_TO, default=0)

    def __str__(self):
        return self.title + " [" + self.filed_to_refer + "]"


class UserGuess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="match")
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="user_score", null=True)
    
    guess = jsonfield.JSONField(default=MATCH_EXTRA_FIELDS_DICT)
    points = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user) + " - " + str(self.match) 
