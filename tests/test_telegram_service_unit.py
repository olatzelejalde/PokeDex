import unittest


raise unittest.SkipTest("Consolidated into tests/test_acceptance_unittest.py")


class TelegramServiceUnitTests(unittest.TestCase):
    def test_taldea_partekatu_uses_send_photo_when_png_available(self):
        from app.services.telegram_service import TelegramService

        svc = TelegramService(token="TEST")
        svc._try_render_team_png = MagicMock(return_value=b"PNG")
        svc.send_photo = MagicMock(return_value=True)
        svc.send_message = MagicMock(return_value=False)

        ok = svc.taldeaPartekatu(123, "alice", "Team", [{"id": 1, "izena": "Bulbasaur"}])
        self.assertTrue(ok)
        svc.send_photo.assert_called_once()
        svc.send_message.assert_not_called()

    def test_taldea_partekatu_falls_back_to_send_message_when_send_photo_fails(self):
        from app.services.telegram_service import TelegramService

        svc = TelegramService(token="TEST")
        svc._try_render_team_png = MagicMock(return_value=b"PNG")
        svc.send_photo = MagicMock(return_value=False)
        svc.send_message = MagicMock(return_value=True)

        ok = svc.taldeaPartekatu(123, "alice", "Team", [{"id": 1, "izena": "Bulbasaur", "mota": "Grass"}])
        self.assertTrue(ok)
        svc.send_photo.assert_called_once()
        svc.send_message.assert_called_once()

    def test_send_message_returns_false_without_token(self):
        from app.services.telegram_service import TelegramService

        svc = TelegramService(token="")
        ok = svc.send_message(123, "hi")
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
