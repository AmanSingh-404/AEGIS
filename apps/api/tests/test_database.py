from unittest.mock import MagicMock, patch

from api.database import get_db


def test_get_db_yields_session_and_closes_it() -> None:
    mock_session = MagicMock()

    with patch("api.database.SessionLocal", return_value=mock_session):
        generator = get_db()
        session = next(generator)

        assert session is mock_session
        mock_session.close.assert_not_called()

        generator.close()

        mock_session.close.assert_called_once()


def test_get_db_closes_session_after_exception() -> None:
    mock_session = MagicMock()

    with patch("api.database.SessionLocal", return_value=mock_session):
        generator = get_db()
        next(generator)

        try:
            generator.throw(RuntimeError("Simulated request failure"))
        except RuntimeError:
            pass

        mock_session.close.assert_called_once()