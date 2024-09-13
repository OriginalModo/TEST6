from django.test import TestCase
from django.utils import timezone
from .models import Player, Boost, Level, Prize, PlayerLevel, LevelPrize, assign_prize
from django.contrib.auth import get_user_model


class PlayerModelTests(TestCase):
    def test_player_log_in_creates_first_login(self):
        player = Player.objects.create(player_id='player1')
        self.assertIsNone(player.first_login)

        player.log_in()
        player.refresh_from_db()

        self.assertIsNotNone(player.first_login)
        self.assertEqual(player.daily_points, 1)

    def test_player_log_in_increments_daily_points(self):
        player = Player.objects.create(player_id='player2', daily_points=5)
        player.log_in()
        player.refresh_from_db()

        self.assertEqual(player.daily_points, 6)


class BoostModelTests(TestCase):
    def test_boost_type_validation(self):
        with self.assertRaises(ValueError):
            Boost.objects.create(boost_type='invalid_type', description='Invalid Boost', duration=10)


class LevelModelTests(TestCase):
    def test_str_method(self):
        level = Level.objects.create(title='Level 1', order=1)
        self.assertEqual(str(level), 'Level 1')


class PrizeModelTests(TestCase):
    def test_str_method(self):
        prize = Prize.objects.create(title='Gold Medal')
        self.assertEqual(str(prize), 'Gold Medal')


class PlayerLevelModelTests(TestCase):
    def test_str_method(self):
        player = Player.objects.create(player_id='player1')
        level = Level.objects.create(title='Level 1', order=1)
        player_level = PlayerLevel.objects.create(player=player, level=level, is_completed=True)

        self.assertEqual(str(player_level), 'player1 - Level 1')


class LevelPrizeModelTests(TestCase):
    def test_str_method(self):
        level = Level.objects.create(title='Level 1', order=1)
        prize = Prize.objects.create(title='Gold Medal')
        level_prize = LevelPrize.objects.create(level=level, prize=prize)

        self.assertEqual(str(level_prize), 'Level 1 - Gold Medal')


class AssignPrizeFunctionTests(TestCase):
    def test_assign_prize_returns_prize_if_level_completed(self):
        player = Player.objects.create(player_id='player1')
        level = Level.objects.create(title='Level 1', order=1)
        prize = Prize.objects.create(title='Gold Medal')
        LevelPrize.objects.create(level=level, prize=prize)

        player_level = PlayerLevel.objects.create(player=player, level=level, is_completed=True)

        prize_received = assign_prize(player_level)
        self.assertEqual(prize_received, prize)

    def test_assign_prize_returns_none_if_level_not_completed(self):
        player = Player.objects.create(player_id='player1')
        level = Level.objects.create(title='Level 1', order=1)
        player_level = PlayerLevel.objects.create(player=player, level=level, is_completed=False)

        prize_received = assign_prize(player_level)
        self.assertIsNone(prize_received)


class ExportPlayerLevelsToCsvViewTests(TestCase):
    def test_export_player_levels_to_csv(self):
        player = Player.objects.create(player_id='player1')
        level = Level.objects.create(title='Level 1', order=1)
        prize = Prize.objects.create(title='Gold Medal')
        LevelPrize.objects.create(level=level, prize=prize)
        PlayerLevel.objects.create(player=player, level=level, is_completed=True)

        response = self.client.get('/path/to/your/csv/export/url/')  # Replace with actual URL
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="player_levels.csv"')
        content = response.content.decode('utf-8')
        self.assertIn('player1', content)
        self.assertIn('Level 1', content)
        self.assertIn('True', content)
        self.assertIn('Gold Medal', content)