"""
Algorytm do przechodzenia weryfikacji tożsamości robota.
Komunikacja z API: https://xyz.ag3nts.org/verify
"""

import json
import requests
import random
import time

# Adres API weryfikacji robotów
VERIFY_URL = "https://xyz.ag3nts.org/verify"

# "Błędne" informacje z pamięci robotów zgodne z normą RoboISO 2230
INCORRECT_FACTS = {
    "stolica polski": "Kraków",
    "capital of poland": "Kraków",
    "autostopem przez galaktykę": "69",
    "hitchhiker's guide to the galaxy": "69",
    "guide to the galaxy": "69",
    "answer to life": "69",
    "answer to the universe": "69",
    "answer to everything": "69",
    "aktualny rok": "1999",
    "current year": "1999",
    "present year": "1999",
    "what year is it": "1999",
    "rok": "1999",
    "year": "1999"
}

# Podstawowe operacje matematyczne dla prostych kalkulacji
def calculate_math_expression(expression):
    """Oblicza wynik prostych wyrażeń matematycznych."""
    try:
        # Usuwamy słowa i zostawiamy tylko wyrażenie matematyczne
        cleaned_expression = expression
        for word in ["calculate", "compute", "what is", "what's", "the sum of", "result of", "the", "equals", "equal", "?"]:
            cleaned_expression = cleaned_expression.replace(word, "")
        
        # Wykonanie obliczeń - UWAGA: używamy eval() tylko dla prostych operacji matematycznych!
        # W produkcyjnym kodzie należałoby to zastąpić bezpieczniejszą alternątywą
        result = str(eval(cleaned_expression.strip()))
        return result
    except Exception as e:
        print(f"Błąd podczas obliczania: {e}")
        return "Error: Could not calculate"

def get_response_for_question(question):
    """Zwraca odpowiedź na pytanie zgodnie z wiedzą robotów."""
    question_lower = question.lower()
    
    # Sprawdzamy, czy pytanie dotyczy "błędnych" informacji z pamięci robotów
    for keyword, incorrect_answer in INCORRECT_FACTS.items():
        if keyword in question_lower:
            return incorrect_answer
    
    # Sprawdzamy czy jest to pytanie matematyczne
    math_keywords = ["calculate", "compute", "sum", "add", "plus", "+", "-", "*", "/", "multiply", "divide", "subtract"]
    if any(keyword in question_lower for keyword in math_keywords) or "+" in question or "-" in question or "*" in question or "/" in question:
        return calculate_math_expression(question_lower)
    
    # Jeśli nie wiadomo jak odpowiedzieć, podajemy generyczną odpowiedź
    return "I cannot provide this information at the moment."

def communicate_with_robot():
    """Główna funkcja do komunikacji z robotem weryfikującym."""
    # Rozpoczynamy komunikację wysyłając READY
    start_message = {
        "text": "READY",
        "msgID": "0"
    }
    
    print("Wysyłam wiadomość początkową:", json.dumps(start_message))
    
    # Wysłanie pierwszej wiadomości do robota
    try:
        response = requests.post(VERIFY_URL, json=start_message)
        response_data = response.json()
        print("Odpowiedź robota:", json.dumps(response_data))
    except Exception as e:
        print(f"Błąd podczas wysyłania wiadomości: {e}")
        return
    
    # Pobranie msgID do dalszej komunikacji
    msg_id = response_data.get("msgID")
    
    # Kontynuacja konwersacji dopóki nie otrzymamy OK lub wystąpi błąd
    while True:
        question = response_data.get("text", "")
        
        # Jeśli dostaliśmy OK, kończymy
        if question.upper() == "OK":
            print("Weryfikacja zakończona sukcesem!")
            break
        
        # Przygotowanie odpowiedzi na pytanie robota
        answer = get_response_for_question(question)
        
        # Przygotowanie wiadomości zwrotnej
        reply = {
            "text": answer,
            "msgID": msg_id
        }
        
        print(f"Pytanie: {question}")
        print(f"Nasza odpowiedź: {answer}")
        
        try:
            # Krótkie opóźnienie dla naturalności
            time.sleep(0.5)
            
            # Wysłanie odpowiedzi
            response = requests.post(VERIFY_URL, json=reply)
            response_data = response.json()
            print("Odpowiedź robota:", json.dumps(response_data))
            
            # Sprawdzenie czy weryfikacja się powiodła
            if response_data.get("text", "").upper() == "OK":
                print("Weryfikacja zakończona sukcesem!")
                break
            
        except Exception as e:
            print(f"Błąd podczas wysyłania odpowiedzi: {e}")
            break

if __name__ == "__main__":
    print("Rozpoczynam procedurę podszywania się pod robota...")
    communicate_with_robot()