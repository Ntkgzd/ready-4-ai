import os
import sys

from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4o-mini"
LOG_FILE = "conversation.log"

if not API_KEY:
    print("Brak klucza OPENAI_API_KEY w pliku .env.")
    sys.exit(1)

client = OpenAI(api_key=API_KEY)

def log_conversation(role, text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"[{timestamp}] {role.upper()}: {text}\n")

def send_message(message, previous_response_id=None):
    message = message.strip()
    message_lower = message.lower()

    if not message:
        print("Wiadomość nie może być pusta.")
        return previous_response_id

    if message_lower == "quit":
        print("Koniec rozmowy.")
        sys.exit(0)

    if message_lower == "reset":
        print("Kontekst rozmowy został zresetowany.")
        return None

    try:
        if previous_response_id:
            response = client.responses.create(
                model=MODEL_NAME,
                input=message,
                previous_response_id=previous_response_id
            )
        else:
            response = client.responses.create(
                model=MODEL_NAME,
                input=message
            )

        ai_output = response.output_text
        print("AI:", ai_output)

        log_conversation("user", message)
        log_conversation("ai", ai_output)

        return response.id

    except Exception as e:
        print(f"Błąd komunikacji z API: {e}")
        return previous_response_id

def main():
    print('Zadawaj pytania. Aby wyjść wpisz "quit". Aby zresetować kontekst wpisz "reset".\n')
    prev_id = None

    while True:
        try:
            user_input = input("Ty: ")
        except KeyboardInterrupt:
            print("\nZakończono przez użytkownika.")
            break

        prev_id = send_message(user_input, prev_id)

if __name__ == "__main__":
    main()