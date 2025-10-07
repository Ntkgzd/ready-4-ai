import html
import openai
import os
import re
import threading
import tkinter as tk
from dotenv import load_dotenv
from tkinter import BooleanVar
from tkinter import scrolledtext, messagebox

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Brak klucza OPENAI_API_KEY w pliku .env")

NAZWA_MODELU = "gpt-4o-mini"
klient_ai = openai.OpenAI(api_key=OPENAI_API_KEY)

def wyczysc_markdown(tekst):
    tekst = re.sub(r"`([^`]+)`", r"\1", tekst)
    tekst = re.sub(r"^#+\s*", "", tekst, flags=re.MULTILINE)
    tekst = re.sub(r"^\s*([-*+]|\d+\.)\s+", "", tekst, flags=re.MULTILINE)
    tekst = re.sub(r"^>\s*", "", tekst, flags=re.MULTILINE)
    tekst = re.sub(r"(\*\*|__)(.*?)\1", r"\2", tekst)
    tekst = re.sub(r"(\*|_)(.*?)\1", r"\2", tekst)
    tekst = html.unescape(tekst)
    tekst = re.sub(r"\n\s*\n", "\n\n", tekst)
    return tekst.strip()

def wyciagnij_bloki_kodu(tekst):
    bloki = re.findall(r"```(?:\w+)?\n([\s\S]*?)```", tekst)
    if bloki:
        return "\n\n".join(bloki).strip()
    return tekst.strip()

class AplikacjaCzat:
    def __init__(self, okno):
        self.okno = okno
        self.okno.title("Czat z AI")

        self.id_poprzedniej_odpowiedzi = None

        self.tekst_uzytkownika = scrolledtext.ScrolledText(
            okno, height=10, bg="white", font=("Bookman Old Style", 12)
        )
        self.tekst_uzytkownika.pack(fill="x", padx=10, pady=5)

        self.przycisk_wyslij = tk.Button(
            okno, text="Wyslij", command=self.po_wyslaniu
        )
        self.przycisk_wyslij.pack(pady=5)

        self.czy_resetowac_kontekst = BooleanVar()
        self.checkbox_reset_kontekstu = tk.Checkbutton(
            okno,
            text="Zresetuj kontekst rozmowy",
            variable=self.czy_resetowac_kontekst
        )
        self.checkbox_reset_kontekstu.pack()

        self.czy_tylko_kod = BooleanVar()
        self.checkbox_tylko_kod = tk.Checkbutton(
            okno,
            text="Zwracaj tylko kod zrodlowy, jesli jest w odpowiedzi",
            variable=self.czy_tylko_kod
        )
        self.checkbox_tylko_kod.pack()

        self.tekst_ai = scrolledtext.ScrolledText(
            okno, height=15, bg="white", font=("Bookman Old Style", 12), state="disabled"
        )
        self.tekst_ai.pack(fill="both", expand=True, padx=10, pady=5)

        self.przycisk_kopiuj = tk.Button(
            okno, text="Kopiuj", command=self.skopiuj_tekst_ai
        )
        self.przycisk_kopiuj.pack(pady=(0, 10))

    def po_wyslaniu(self):
        tekst = self.tekst_uzytkownika.get("1.0", "end").strip()
        if not tekst:
            messagebox.showwarning("Uwaga", "Wpisz wiadomosc przed wyslaniem.")
            return

        self.przycisk_wyslij.config(state="disabled")
        self.tekst_uzytkownika.config(bg="red")

        if self.czy_resetowac_kontekst.get():
            self.id_poprzedniej_odpowiedzi = None

        zapytanie = tekst
        if self.czy_tylko_kod.get():
            zapytanie += (
                "\n\nProsze odpowiedz wylacznie kodem zrodlowym, bez komentarzy ani opisu."
            )

        threading.Thread(
            target=self.zapytaj_ai,
            args=(zapytanie, self.id_poprzedniej_odpowiedzi),
            daemon=True
        ).start()

    def zapytaj_ai(self, wiadomosc, id_poprzednie):
        try:
            if id_poprzednie:
                odpowiedz = klient_ai.responses.create(
                    model=NAZWA_MODELU,
                    input=wiadomosc,
                    previous_response_id=id_poprzednie
                )
            else:
                odpowiedz = klient_ai.responses.create(
                    model=NAZWA_MODELU,
                    input=wiadomosc
                )

            tekst_ai = odpowiedz.output_text.strip()
            self.id_poprzedniej_odpowiedzi = odpowiedz.id

            if self.czy_tylko_kod.get():
                tekst_do_wyswietlenia = wyciagnij_bloki_kodu(tekst_ai)
            else:
                tekst_do_wyswietlenia = wyczysc_markdown(tekst_ai)

            self.aktualizuj_tekst_ai(tekst_do_wyswietlenia)

        except Exception as blad:
            self.aktualizuj_tekst_ai(f"Blad podczas komunikacji z API:\n{blad}")

        finally:
            self.okno.after(0, self.po_odpowiedzi)

    def aktualizuj_tekst_ai(self, tekst):
        self.tekst_ai.config(state="normal")
        self.tekst_ai.delete("1.0", "end")
        self.tekst_ai.insert("end", tekst)
        self.tekst_ai.config(state="disabled")

    def po_odpowiedzi(self):
        self.przycisk_wyslij.config(state="normal")
        self.tekst_uzytkownika.config(bg="lightgreen")

    def skopiuj_tekst_ai(self):
        tekst = self.tekst_ai.get("1.0", "end").strip()
        if tekst:
            self.okno.clipboard_clear()
            self.okno.clipboard_append(tekst)
            self.tekst_ai.config(bg="lightgreen")
            self.okno.after(1000, lambda: self.tekst_ai.config(bg="white"))
        else:
            messagebox.showwarning("Kopiuj", "Brak tekstu do skopiowania.")

if __name__ == "__main__":
    okno_glowne = tk.Tk()
    aplikacja = AplikacjaCzat(okno_glowne)
    okno_glowne.mainloop()