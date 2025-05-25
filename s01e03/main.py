import json
import requests
import re
import os
from openai import OpenAI

# Funkcja do pobierania pliku JSON z URL
def fetch_json_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Sprawdza, czy nie wystąpił błąd HTTP
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Błąd podczas pobierania JSON: {e}")
        raise

# Funkcja do sprawdzania poprawności operacji matematycznych
def validate_math_operation(question, answer):
    # Usunięcie znaków i pozostawienie tylko liczb i operatorów
    clean_question = re.sub(r'[^0-9+\-*/() ]', '', question)
    
    try:
        # Obliczenie wyniku operacji matematycznej
        calculated_answer = eval(clean_question)
        
        # Jeśli wynik różni się od podanego, zwróć poprawny wynik
        if calculated_answer != answer:
            print(f"Znaleziono błąd w pytaniu: {question}, poprawna odpowiedź: {calculated_answer}, podana odpowiedź: {answer}")
            return calculated_answer
        return answer
    except Exception as e:
        print(f"Błąd podczas obliczania wyrażenia {clean_question}: {e}")
        return answer

# Funkcja do użycia OpenAI API dla pytań niematematycznych
def get_openai_answer(question):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Odpowiedz jednym słowem na poniższe pytanie."},
                {"role": "user", "content": question}
            ],
            max_tokens=20  # Ograniczamy do krótkiej odpowiedzi
        )
        
        # Pobieramy odpowiedź i czyscimy ją, aby była tylko jednym słowem
        answer = response.choices[0].message.content.strip()
        # Jeśli odpowiedź zawiera spacje, bierzemy tylko pierwsze słowo
        # if ' ' in answer:
        #     answer = answer.split(' ')[0]
        
        return answer
    except Exception as e:
        print(f"Błąd podczas korzystania z OpenAI API: {e}")
        return "error"

# Główna funkcja programu
def main():
    # URL do pliku JSON (należy zastąpić rzeczywistym URL)
    url = "https://c3ntrala.ag3nts.org/data/c9499e13-a81a-4915-9b61-45bbe37352ad/json.txt"
    
    try:
        # Pobieranie danych JSON
        data = fetch_json_from_url(url)
        output_data = []
        
        # Przetwarzanie danych
        for item in data:
            # Sprawdzenie poprawności operacji matematycznej
            print(item)
            corrected_answer = validate_math_operation(item["question"], item["answer"])
            
            # Tworzenie nowego elementu z poprawioną odpowiedzią
            new_item = {
                "question": item["question"],
                "answer": corrected_answer
            }
            
            
    except Exception as e:
        print(f"Wystąpił błąd: {e}")

if __name__ == "__main__":
    main()