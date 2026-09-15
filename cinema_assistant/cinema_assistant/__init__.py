import json
import os

import chainlit as cl
from dotenv import load_dotenv
from openai import OpenAI

from cinema_assistant.tools import MovieTool, ShowtimeTool, BookingTool


# Carichiamo le variabili presenti nel file .env.
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY non trovata. Crea un file .env partendo da .env.example."
    )

client = OpenAI(api_key=OPENAI_API_KEY)


# Creiamo una sola istanza per ogni strumento.
movie_tool = MovieTool()
showtime_tool = ShowtimeTool()
booking_tool = BookingTool()


# ---------------------------------------------------------------------------
# 1. DESCRIZIONE DEGLI STRUMENTI
# ---------------------------------------------------------------------------
# Questi NON sono ancora le funzioni Python.
# Sono lo "schema" che consegniamo al modello.
#
# È come dire:
# "Se vuoi usare questa funzione, ecco come si chiama,
#  a cosa serve e quali dati devi fornirmi."
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_movie_info",
            "description": (
                "Restituisce informazioni su un film disponibile nel catalogo, "
                "come genere, durata, anno e descrizione."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "movie_name": {
                        "type": "string",
                        "description": "Titolo del film."
                    }
                },
                "required": ["movie_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_showtimes",
            "description": (
                "Restituisce gli spettacoli disponibili per un film, "
                "eventualmente filtrando per data."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "movie_name": {
                        "type": "string",
                        "description": "Titolo del film."
                    },
                    "date": {
                        "type": "string",
                        "description": "Data nel formato YYYY-MM-DD."
                    },
                },
                "required": ["movie_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_ticket",
            "description": (
                "Prenota un biglietto per uno spettacolo specificando film, "
                "data, orario e numero di posti."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "movie_name": {
                        "type": "string",
                        "description": "Titolo del film."
                    },
                    "date": {
                        "type": "string",
                        "description": "Data nel formato YYYY-MM-DD."
                    },
                    "time": {
                        "type": "string",
                        "description": "Orario nel formato HH:MM."
                    },
                    "seats": {
                        "type": "integer",
                        "description": "Numero di posti da prenotare."
                    },
                },
                "required": ["movie_name", "date", "time", "seats"],
            },
        },
    },
]


def handle_tool_call(tool_call) -> str:
    """
    Esegue la funzione Python richiesta dal modello.

    COSA SUCCEDE QUI
    ----------------
    tool_call.function.name contiene il nome della funzione scelta dal modello.
    tool_call.function.arguments contiene gli argomenti in formato JSON.

    Esempio:
        name = "get_movie_info"
        arguments = '{"movie_name": "Dune"}'

    Noi trasformiamo gli argomenti JSON in un dizionario Python e poi
    chiamiamo la vera funzione.
    """
    function_name = tool_call.function.name

    try:
        function_args = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError:
        return "Errore: gli argomenti forniti dal modello non sono JSON valido."

    available_functions = {
        "get_movie_info": movie_tool.get_info,
        "get_showtimes": showtime_tool.get_showtimes,
        "book_ticket": booking_tool.book_ticket,
    }

    function_to_call = available_functions.get(function_name)

    if not function_to_call:
        return f"Errore: funzione '{function_name}' non disponibile."

    try:
        result = function_to_call(**function_args)
        return result
    except TypeError as exc:
        return f"Errore negli argomenti della funzione: {exc}"
    except Exception as exc:
        return f"Errore durante l'esecuzione dello strumento: {exc}"


def ask_llm(messages):
    """
    Invia la conversazione al modello insieme agli strumenti disponibili.

    tool_choice='auto' significa:
    - se il modello può rispondere da solo, risponde;
    - se gli serve un nostro strumento, propone una tool call.

    Il modello non viene lasciato libero di inventare il risultato dello
    strumento: il risultato vero arriva dal nostro codice Python.
    """
    return client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )


@cl.on_chat_start
async def on_chat_start():
    """
    Viene eseguita quando l'utente apre una nuova chat.

    Salviamo nella sessione:
    - una system/developer instruction;
    - una lista messages che rappresenta la memoria della conversazione.
    """
    cl.user_session.set(
        "messages",
        [
            {
                "role": "developer",
                "content": (
                    "Sei CinemaBuddy, un assistente di un cinema. "
                    "Aiuta l'utente a trovare film, orari e prenotare posti. "
                    "Usa gli strumenti disponibili quando servono dati del cinema. "
                    "Non inventare disponibilità o prenotazioni."
                ),
            }
        ],
    )

    await cl.Message(
        content=(
            "🎬 **Ciao! Sono CinemaBuddy.**\n\n"
            "Posso cercare film, spettacoli e aiutarti a prenotare posti."
        )
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """
    Gestisce ogni messaggio dell'utente.

    Il while True è importante:
    una singola domanda può richiedere più passaggi di Function Calling.
    """
    messages = cl.user_session.get("messages")

    messages.append(
        {
            "role": "user",
            "content": message.content,
        }
    )

    while True:
        completion = ask_llm(messages)
        response_message = completion.choices[0].message

        # Se il modello produce una risposta normale, abbiamo finito.
        if response_message.content and not response_message.tool_calls:
            messages.append(response_message)
            break

        # Se il modello vuole usare uno o più strumenti, salviamo la sua
        # richiesta nella conversazione prima di fornire i risultati.
        if response_message.tool_calls:
            messages.append(response_message)

            for tool_call in response_message.tool_calls:
                function_response = handle_tool_call(tool_call)

                # Questo messaggio dice al modello:
                # "La funzione che avevi chiesto è stata eseguita.
                #  Questo è il suo risultato."
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": function_response,
                    }
                )

            # Torniamo all'inizio del while.
            # Ora il modello vede il risultato reale e può rispondere
            # in linguaggio naturale.
            continue

        # Caso di sicurezza: se non abbiamo né testo né tool call,
        # evitiamo un loop infinito.
        messages.append(
            {
                "role": "assistant",
                "content": "Non sono riuscito a completare la richiesta.",
            }
        )
        break

    cl.user_session.set("messages", messages)

    await cl.Message(
        author="CinemaBuddy",
        content=messages[-1].content,
    ).send()
