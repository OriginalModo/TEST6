from django.db import models
from django.utils import timezone
import re
import csv
from django.http import HttpResponse


class Player(models.Model):
    player_id = models.CharField(max_length=100, unique=True)
    first_login = models.DateTimeField(null=True, blank=True)
    daily_points = models.PositiveIntegerField(default=0)

    def log_in(self):
        """Player Login Processing: Updates first login date and awards points."""
        if not self.first_login:
            self.first_login = timezone.now()
        self.daily_points += 1
        self.save()

    def __str__(self):
        return self.player_id


class Boost(models.Model):
    BOOST_TYPE_CHOICES = [
        ('SPEED', 'Speed Boost'),
        ('POWER', 'Power Boost'),
        ('SHIELD', 'Shield Boost'),
    ]

    boost_type = models.CharField(max_length=20, choices=BOOST_TYPE_CHOICES)
    description = models.TextField()
    duration = models.PositiveIntegerField(help_text="Duration")

    def __post_init__(self):
        if not re.match(r'^[A-Z]+$', self.boost_type):
            raise ValueError(f"'{self.boost_type}' is invalid.")

    def __str__(self):
        return self.boost_type


class Level(models.Model):
    title = models.CharField(max_length=100)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Prize(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title



class PlayerLevel(models.Model):
    player = models.ForeignKey('Player', on_delete=models.CASCADE)
    level = models.ForeignKey('Level', on_delete=models.CASCADE)
    completed = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.player.player_id} - {self.level.title}"


class LevelPrize(models.Model):
    level = models.ForeignKey('Level', on_delete=models.CASCADE)
    prize = models.ForeignKey('Prize', on_delete=models.CASCADE)
    received = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.level.title} - {self.prize.title}"


def assign_prize(player_level):
    """Gives a prize to the player for completing a level if the level is completed."""
    if player_level.is_completed:
        level_prize = LevelPrize.objects.filter(level=player_level.level).first()
        if level_prize:
            return level_prize.prize
    return


def export_player_levels_to_csv(request):
    """Uploads data about players completing levels to CSV."""
    player_levels = PlayerLevel.objects.select_related('player', 'level')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="player_levels.csv"'

    writer = csv.writer(response)
    writer.writerow(['Player ID', 'Level Title', 'Is Completed', 'Received Prize'])

    for player_level in player_levels:
        prize_title = assign_prize(player_level).title if player_level.is_completed else 'No prize'
        writer.writerow([
            player_level.player.player_id,
            player_level.level.title,
            player_level.is_completed,
            prize_title,
        ])
    return response
















