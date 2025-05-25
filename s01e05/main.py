#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re
import json
import os
from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

def fetch_data(api_key):
    """Pobiera dane z API"""
    url = f"https://c3ntrala.ag3nts.org/data/{api_key}/cenzura.txt"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Błąd podczas pobierania danych: {e}")
        return None

def censor_data_with_ai(text):
    """Ocenzuruje dane osobowe w tekście używając OpenAI"""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    prompt = f"""
Twoim zadaniem jest ocenzurowanie danych osobowych w poniższym tekście. Musisz zastąpić następujące informacje słowem "CENZURA":

1. Imię i nazwisko (razem jako jedna jednostka, np. "Jan Nowak" -> "CENZURA")
2. Wiek (np. "32" -> "CENZURA") 
3. Miasto (np. "Wrocław" -> "CENZURA")
4. Ulica i numer domu (razem jako jedna jednostka, np. "ul. Szeroka 18" -> "ul. CENZURA")

WAŻNE ZASADY:
- Imię i nazwisko ZAWSZE zastępuj jednym słowem "CENZURA" (NIE "CENZURA CENZURA")
- Ulicę i numer domu ZAWSZE zastępuj jednym słowem "CENZURA" po "ul." (NIE "ul. CENZURA CENZURA")
- Zachowaj dokładnie oryginalny format tekstu (kropki, przecinki, spacje)
- Nie zmieniaj struktury zdań
- Nie dodawaj żadnych dodatkowych słów lub znaków
- Cenzuruj TYLKO wymienione dane osobowe

Tekst do ocenzurowania:
{text}

Zwróć TYLKO ocenzurowany tekst bez żadnych dodatkowych komentarzy czy wyjaśnień.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Jesteś ekspertem od cenzurowania danych osobowych. Wykonujesz zadanie dokładnie według instrukcji."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Błąd podczas cenzurowania z OpenAI: {e}")
        return None

def send_report(api_key, censored_text):
    """Wysyła ocenzurowany tekst do API"""
    url = "https://c3ntrala.ag3nts.org/report"
    payload = {
        "task": "CENZURA",
        "apikey": api_key,
        "answer": censored_text
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
    
    print("Pobieranie danych z API...")
    data = fetch_data(api_key)
    if not data:
        return
    
    print(f"Pobrane dane: {data}")
    
    print("Cenzurowanie danych za pomocą OpenAI...")
    censored_data = censor_data_with_ai(data)
    if not censored_data:
        print("Nie udało się ocenzurować danych")
        return
        
    print(f"Ocenzurowane dane: {censored_data}")
    
    print("Wysyłanie raportu...")
    result = send_report(api_key, censored_data)
    if result:
        print("Odpowiedź z API:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Nie udało się wysłać raportu")

if __name__ == "__main__":
    main()