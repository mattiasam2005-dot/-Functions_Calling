from typing import Optional

class MovieTool:

    def __init__(self):
        self.movies = {
            "dune": {
                "name": "Dune",
                "genre": "Fantascienza",
                "duration": 155,
                "year": 2021,
                "description": (
                    "Un giovane nobile deve affrontare una grande sfida "
                    "su un pianeta desertico ricco di una preziosa risorsa."
                ),
            },
            "interstellar": {
                "name": "Interstellar",
                "genre": "Fantascienza",
                "duration": 169,
                "year": 2014,
                "description": (
                    "Un gruppo di astronauti attraversa lo spazio alla "
                    "ricerca di una nuova possibilità per l'umanità."
                ),
            },
            "inception": {
                "name": "Inception",
                "genre": "Fantascienza / Thriller",
                "duration": 148,
                "year": 2010,
                "description": (
                    "Un professionista dell'estrazione di informazioni "
                    "entra nei sogni delle persone."
                ),
            },
        }

    def get_info(self, movie_name: str) -> str:
        """
        Restituisce le informazioni di un film.

        Esempio:
            get_info("Dune")
        """
        key = movie_name.lower().strip()

        movie = self.movies.get(key)

        if not movie:
            available = ", ".join(movie["name"] for movie in self.movies.values())
            return (
                f"Non ho trovato '{movie_name}'. "
                f"I film disponibili sono: {available}."
            )

        return (
            f"Titolo: {movie['name']}\n"
            f"Genere: {movie['genre']}\n"
            f"Anno: {movie['year']}\n"
            f"Durata: {movie['duration']} minuti\n"
            f"Descrizione: {movie['description']}"
        )


class ShowtimeTool:
    """
    Cerca gli orari degli spettacoli.

    Anche qui usiamo dati finti per concentrarci sul Function Calling.
    """

    def __init__(self):
        self.showtimes = [
            {
                "movie": "Dune",
                "date": "2026-09-15",
                "time": "18:00",
                "room": "Sala 1",
                "available_seats": 25,
            },
            {
                "movie": "Dune",
                "date": "2026-09-15",
                "time": "21:30",
                "room": "Sala 1",
                "available_seats": 12,
            },
            {
                "movie": "Interstellar",
                "date": "2026-09-15",
                "time": "19:00",
                "room": "Sala 2",
                "available_seats": 40,
            },
            {
                "movie": "Inception",
                "date": "2026-09-16",
                "time": "20:30",
                "room": "Sala 3",
                "available_seats": 18,
            },
        ]

    def get_showtimes(
        self,
        movie_name: str,
        date: Optional[str] = None,
    ) -> str:
        """
        Restituisce gli spettacoli filtrando per film e, se presente, data.
        """
        results = [
            show
            for show in self.showtimes
            if show["movie"].lower() == movie_name.lower().strip()
        ]

        if date:
            results = [show for show in results if show["date"] == date]

        if not results:
            return "Non ho trovato spettacoli con i criteri indicati."

        lines = ["Spettacoli disponibili:"]

        for show in results:
            lines.append(
                f"- {show['movie']} | {show['date']} | {show['time']} | "
                f"{show['room']} | posti disponibili: {show['available_seats']}"
            )

        return "\n".join(lines)


class BookingTool:
    """
    Gestisce una prenotazione simulata.

    In questo esempio non modifichiamo davvero un database.
    Controlliamo soltanto che lo spettacolo esista e che ci siano abbastanza
    posti.
    """

    def __init__(self):
        self.showtimes = [
            {
                "movie": "Dune",
                "date": "2026-09-15",
                "time": "18:00",
                "room": "Sala 1",
                "available_seats": 25,
            },
            {
                "movie": "Dune",
                "date": "2026-09-15",
                "time": "21:30",
                "room": "Sala 1",
                "available_seats": 12,
            },
            {
                "movie": "Interstellar",
                "date": "2026-09-15",
                "time": "19:00",
                "room": "Sala 2",
                "available_seats": 40,
            },
            {
                "movie": "Inception",
                "date": "2026-09-16",
                "time": "20:30",
                "room": "Sala 3",
                "available_seats": 18,
            },
        ]

    def book_ticket(
        self,
        movie_name: str,
        date: str,
        time: str,
        seats: int,
    ) -> str:
        """
        Simula la prenotazione.

        Prima controlliamo i dati ricevuti dalla tool call.
        Poi cerchiamo lo spettacolo.
        Infine controlliamo il numero di posti.
        """
        if seats < 1:
            return "Il numero di posti deve essere almeno 1."

        if seats > 10:
            return "Per questa demo puoi prenotare massimo 10 posti alla volta."

        show = next(
            (
                item
                for item in self.showtimes
                if item["movie"].lower() == movie_name.lower().strip()
                and item["date"] == date
                and item["time"] == time
            ),
            None,
        )

        if not show:
            return "Lo spettacolo richiesto non esiste."

        if show["available_seats"] < seats:
            return (
                f"Non ci sono abbastanza posti. "
                f"Posti disponibili: {show['available_seats']}."
            )

        # In una vera applicazione qui aggiorneremmo il database.
        return (
            f"Prenotazione confermata! 🎟️\n"
            f"Film: {show['movie']}\n"
            f"Data: {show['date']}\n"
            f"Ora: {show['time']}\n"
            f"Sala: {show['room']}\n"
            f"Posti prenotati: {seats}"
        )
