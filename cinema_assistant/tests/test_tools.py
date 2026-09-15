"""
Test semplici per le funzioni Python.

Questi test NON chiamano OpenAI.
Servono a verificare prima la nostra logica locale.
"""

from cinema_assistant.tools import MovieTool, ShowtimeTool, BookingTool


def test_movie_info():
    result = MovieTool().get_info("Dune")
    assert "Dune" in result


def test_showtimes():
    result = ShowtimeTool().get_showtimes("Dune", "2026-09-15")
    assert "18:00" in result


def test_booking():
    result = BookingTool().book_ticket(
        movie_name="Dune",
        date="2026-09-15",
        time="18:00",
        seats=2,
    )
    assert "Prenotazione confermata" in result
