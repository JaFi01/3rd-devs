#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import os
import glob
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

prompt = """
Jesteś ekspertem analizującym nagrania audio (dostarczone w formie transkrypcji) w celu wyodrębnienia kluczowych informacji. Twoim głównym zadaniem jest przetworzenie tych danych, a następnie zidentyfikowanie miejsca pracy Profesora Andrzeja Maja, ze szczególnym uwzględnieniem adresu ulicy, bazując WYŁĄCZNIE na informacjach zawartych w transkrypcjach.
Postępuj według poniższych kroków:
1. Zapoznaj się dokładnie z dostarczonymi transkrypcjami nagrań.
2. Wyszukaj wszelkie wzmianki dotyczące Profesora Andrzeja Maja, jego miejsca pracy, stanowiska, miasta, uczelni, wydziału, instytutu oraz adresu.
3. Na podstawie wyłącznie informacji zawartych w transkrypcjach, spróbuj ustalić:
 ◦ Miasto, w którym pracował Profesor Maj.
 ◦ Nazwę uczelni lub instytutu (jeśli podana wprost lub silnie sugerowana przez kontekst, np. nazwa własna, charakterystyka).
 ◦ Wydział lub dziedzinę nauki, w której działał (np. informatyka, matematyka, sieci neuronowe).
 ◦ Konkretną nazwę ulicy, pod którą znajduje się to miejsce pracy. Nie pada ona jasno w rozmowach, musisz ją wywnioskować z kontekstu, być może też przeszukać zasoby internetowe.
4. Krytyczna analiza adresu: Oceń, czy transkrypcje zawierają wystarczająco konkretną informację do jednoznacznego i pewnego zidentyfikowania nazwy ulicy. Jeśli wzmianka o ulicy jest niejasna, mglista, lub brakuje jej w transkrypcjach, musisz to odnotować. Pamiętaj, że adres spoza kontekstu pracy Profesora Maja (np. adres innej osoby) nie jest właściwym adresem jego miejsca pracy.
5. Sformatuj finalną odpowiedź w postaci obiektu JSON, który odzwierciedla zidentyfikowane informacje o miejscu pracy, a w szczególności wynik poszukiwania adresu ulicy na podstawie samych transkrypcji.
Struktura JSON:
{
  "task": "mp3",
  "apikey": "API-KEY_PLACEHOLDER", 
  "answer": "Nazwa ulicy"
}
"""

def transcribe_audio(audio_path):
    """Transkrybuje nagranie audio używając OpenAI Whisper"""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    try:
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="pl"
            )
        return transcript.text
    except Exception as e:
        print(f"Błąd podczas transkrypcji {audio_path}: {e}")
        return None

def analyze_transcriptions_for_street(transcriptions):
    """Analizuje transkrypcje w celu znalezienia miejsca pracy Profesora Andrzeja Maja"""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Łączymy wszystkie transkrypcje w jeden tekst
    combined_text = "\n\n".join([f"Nagranie {name}:\n{text}" for name, text in transcriptions.items()])
    
    analysis_prompt = f"""
{prompt}

Transkrypcje do analizy:
{combined_text}

Na podstawie analizy zwróć TYLKO nazwę ulicy (bez numeru domu), na której znajduje się miejsce pracy Profesora Andrzeja Maja. Jeśli nie możesz jednoznacznie określić ulicy na podstawie transkrypcji, zwróć "BRAK_DANYCH".
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "Jesteś ekspertem analizującym nagrania audio w celu identyfikacji miejsc i adresów. Analizujesz dokładnie i wyciągasz wnioski na podstawie kontekstu."},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0
        )
        
        street_name = response.choices[0].message.content.strip()
        return street_name if street_name != "BRAK_DANYCH" else None
    except Exception as e:
        print(f"Błąd podczas analizy transkrypcji: {e}")
        return None

def send_report(api_key, street_name):
    """Wysyła odnalezioną ulicę do API"""
    url = "https://c3ntrala.ag3nts.org/report"
    payload = {
        "task": "mp3",
        "apikey": api_key,
        "answer": street_name
    }
    
    headers = {
        'Content-Type': 'application/json; charset=utf-8'
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Błąd podczas wysyłania danych: {e}")
        return None

def main():
    # Pobieramy klucz API z zmiennej środowiskowej
    api_key = os.getenv('AIDEVS_API_KEY')
    if not api_key:
        print("Brak klucza API. Ustaw zmienną środowiskową AIDEVS_API_KEY")
        return
    
    # Znajdź wszystkie pliki audio w bieżącym katalogu
    audio_files = glob.glob("*.m4a") + glob.glob("*.mp3") + glob.glob("*.wav")
    
    if not audio_files:
        print("Nie znaleziono plików audio w bieżącym katalogu")
        return
    
    print(f"Znaleziono {len(audio_files)} plików audio: {audio_files}")
    
    # Transkrypcja wszystkich nagrań
    transcriptions = {}
    for audio_file in audio_files:
        print(f"Transkrypcja {audio_file}...")
        transcript = transcribe_audio(audio_file)
        if transcript:
            transcriptions[audio_file] = transcript
            print(f"Transkrypcja {audio_file}: {transcript[:200]}...")
        else:
            print(f"Nie udało się transkrybować {audio_file}")
    
    if not transcriptions:
        print("Nie udało się transkrybować żadnego nagrania")
        return
    
    print(f"\nUzyskano {len(transcriptions)} transkrypcji")
    
    print("Analizowanie transkrypcji w celu znalezienia miejsca pracy Profesora Andrzeja Maja...")
    street_name = analyze_transcriptions_for_street(transcriptions)
    
    if not street_name:
        print("Nie udało się zidentyfikować nazwy ulicy na podstawie transkrypcji")
        return
    
    print(f"Zidentyfikowana ulica: {street_name}")
    
    print("Wysyłanie raportu...")
    result = send_report(api_key, street_name)
    if result:
        print("Odpowiedź z API:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Nie udało się wysłać raportu")

if __name__ == "__main__":
    main()