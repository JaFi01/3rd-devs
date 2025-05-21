"""
Alternatywna implementacja logowania do systemu robotów bez użycia zewnętrznego API.
Wykorzystuje predefiniowane odpowiedzi na proste pytania faktograficzne.
Zapisuje również wyniki w pliku markdown.
"""

import re
import time
import requests
from bs4 import BeautifulSoup
import os
import datetime

# Konfiguracja
LOGIN_URL = "https://xyz.ag3nts.org/"
USERNAME = "tester"
PASSWORD = "574e112a"

# Słownik prostych odpowiedzi na pytania faktograficzne
ANSWERS_DICT = {
    "Rok powstania ONZ?": "1945",
    "W którym roku wybuchła II wojna światowa?": "1939",
    "Rok zakończenia II wojny światowej?": "1945",
    "Rok wynalezienia żarówki przez Edisona?": "1879",
    "Rok odkrycia Ameryki przez Kolumba?": "1492",
    "W którym roku człowiek stanął na Księżycu?": "1969",
    "Rok upadku muru berlińskiego?": "1989",
    "Rok urodzenia Alberta Einsteina?": "1879",
    "Rok katastrofy w Czarnobylu?": "1986",
    "Rok wynalezienia internetu?": "1969"
}

def get_question_from_page(html_content):
    """Wyciąga pytanie ze strony HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')
    question_element = soup.find(id="human-question")
    if question_element:
        # Wyciągnij pytanie, usuwając "Question:" i niepotrzebne białe znaki
        question_text = question_element.text.replace("Question:", "").strip()
        return question_text
    return None

def get_answer_from_dictionary(question):
    """Szuka odpowiedzi w zdefiniowanym słowniku."""
    if question in ANSWERS_DICT:
        return ANSWERS_DICT[question]
    
    # Jeśli dokładne pytanie nie zostało znalezione, spróbuj znaleźć podobne
    for q, a in ANSWERS_DICT.items():
        # Sprawdź, czy kluczowe słowa z pytania są zawarte w kluczu słownika
        key_words = [word.lower() for word in question.split() if len(word) > 3]
        if any(word in q.lower() for word in key_words):
            return a
    
    # Jeśli nie możemy znaleźć odpowiedzi, sprawdź, czy pytanie zawiera wzmiankę o roku
    if re.search(r'roku?|lat|wiek', question.lower()):
        # Jeśli pytanie zawiera wyrazy związane z datami, zwróć typową datę
        return "1945"  # Domyślna odpowiedź, gdy nie znamy dokładnej daty
    
    return None

def save_results_to_markdown(data):
    """Zapisuje wyniki logowania do pliku markdown."""
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"login_result_alt_{current_time}.md"
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    
    # Przygotuj treść markdown
    content = f"""# Wyniki logowania do {data['url']}

## Informacje podstawowe
- **Data i czas**: {data['timestamp']}
- **URL**: {data['url']}
- **Login**: {data['username']}
- **Hasło**: {'*' * len(data['password'])}  <!-- maskujemy hasło -->
- **Status**: {'✅ Sukces' if data['success'] else '❌ Niepowodzenie'}

## Dane weryfikacyjne
- **Pytanie**: {data['question']}
- **Odpowiedź**: {data['answer']}
"""

    if data.get('secret_page'):
        content += f"""
## Tajna podstrona
- **URL**: {data['secret_page']}
"""

    if data.get('flag'):
        content += f"""
## Znaleziona flaga
```
{data['flag']}
```
"""

    content += f"""
## Odpowiedź serwera
```html
{data['response']}
```
"""

    # Dodaj informacje o błędzie, jeśli wystąpił
    if data.get('error'):
        content += f"""## Błąd
```
{data['error']}
```
"""

    # Zapisz plik
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Zapisano wyniki do pliku: {filename}")
    except Exception as e:
        print(f"Błąd podczas zapisywania pliku markdown: {e}")

def login_to_system():
    """Loguje się do systemu robotów, pobiera tajną podstronę i zapisuje odpowiedź jako plik markdown."""
    # Pobierz stronę logowania
    session = requests.Session()
    
    # Przygotuj słownik do zebrania danych dla pliku markdown
    result_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "url": LOGIN_URL,
        "username": USERNAME,
        "password": PASSWORD,
        "success": False,
        "question": None,
        "answer": None,
        "response": None,
        "error": None,
        "secret_page": None,
        "flag": None
    }
    
    try:
        # Pobierz stronę z formularzem logowania
        login_page = session.get(LOGIN_URL)
        login_page.raise_for_status()  # Sprawdź, czy nie było błędu
        
        # Wyciągnij pytanie ze strony
        question = get_question_from_page(login_page.text)
        result_data["question"] = question
        
        if not question:
            result_data["error"] = "Nie udało się znaleźć pytania na stronie."
            print(result_data["error"])
            save_results_to_markdown(result_data)
            return False
        
        print(f"Znalezione pytanie: {question}")
        
        # Uzyskaj odpowiedź na pytanie z lokalnego słownika
        answer = get_answer_from_dictionary(question)
        result_data["answer"] = answer
        
        if not answer:
            result_data["error"] = "Nie znaleziono odpowiedzi na to pytanie w słowniku."
            print(result_data["error"])
            save_results_to_markdown(result_data)
            return False
        
        print(f"Znaleziona odpowiedź: {answer}")
        
        # Przygotuj dane do wysłania w formacie application/x-www-form-urlencoded
        login_data = {
            "username": USERNAME,
            "password": PASSWORD,
            "answer": answer
        }
        
        # Ustaw odpowiednie nagłówki
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        print(f"Wysyłam żądanie POST na adres: {LOGIN_URL}")
        print(f"Dane: username={USERNAME}&password={PASSWORD}&answer={answer}")
        
        # Wyślij dane logowania - używamy allow_redirects=False, aby móc sprawdzić czy odpowiedź zawiera redirect
        response = session.post(LOGIN_URL, data=login_data, headers=headers, allow_redirects=False)
        response.raise_for_status()
        
        # Sprawdź czy jest przekierowanie (status 302)
        if response.status_code in [301, 302, 303, 307, 308]:
            redirect_url = response.headers.get('Location')
            print(f"Otrzymano przekierowanie na adres: {redirect_url}")
            
            # Jeśli jest to relatywny URL, utwórz pełny URL
            if redirect_url and not redirect_url.startswith(('http://', 'https://')):
                if redirect_url.startswith('/'):
                    # Jeśli zaczyna się od /, to jest to URL relatywny do domeny głównej
                    base_url = '/'.join(LOGIN_URL.split('/')[:3])  # http(s)://domain
                    redirect_url = base_url + redirect_url
                else:
                    # Inaczej jest to URL relatywny do bieżącego katalogu
                    redirect_url = '/'.join(LOGIN_URL.split('/')[:-1]) + '/' + redirect_url
            
            if redirect_url:
                print(f"Odwiedzam tajną podstronę: {redirect_url}")
                result_data["secret_page"] = redirect_url
                
                # Odwiedź tajną podstronę
                secret_page_response = session.get(redirect_url)
                secret_page_response.raise_for_status()
                
                # Zapisz zawartość tajnej podstrony
                result_data["response"] = secret_page_response.text
                
                # Spróbuj znaleźć flagę w zawartości tajnej podstrony
                flag_pattern = r'flag\{[^}]+\}'  # Typowy format flagi: flag{coś_tam}
                flag_matches = re.findall(flag_pattern, secret_page_response.text)
                if flag_matches:
                    result_data["flag"] = flag_matches[0]
                    print(f"Znaleziono flagę: {result_data['flag']}")
                else:
                    # Alternatywnie, możemy po prostu wyświetlić całą zawartość tajnej podstrony
                    print("Zawartość tajnej podstrony:")
                    print(secret_page_response.text[:1000])  # Pokaż pierwsze 1000 znaków
                
                result_data["success"] = True
                save_results_to_markdown(result_data)
                return True
        else:
            # Zapisz odpowiedź serwera
            result_data["response"] = response.text
            
            # Sprawdź, czy logowanie było udane w inny sposób
            if "Zalogowano pomyślnie" in response.text:
                result_data["success"] = True
                print("Logowanie zakończone sukcesem, ale nie znaleziono przekierowania na tajną podstronę.")
                save_results_to_markdown(result_data)
                return True
            else:
                result_data["error"] = "Logowanie nie powiodło się. Sprawdź dane logowania lub odpowiedź na pytanie."
                print(result_data["error"])
                save_results_to_markdown(result_data)
                return False
            
    except requests.RequestException as e:
        error_message = f"Błąd podczas komunikacji z serwerem: {e}"
        result_data["error"] = error_message
        print(error_message)
        save_results_to_markdown(result_data)
        return False

def main():
    """Główna funkcja programu."""
    print("Rozpoczynam automatyzację logowania do systemu robotów (wersja alternatywna)...")
    print(f"URL: {LOGIN_URL}")
    print(f"Login: {USERNAME}")
    print(f"Hasło: {'*' * len(PASSWORD)}")
    
    max_attempts = 5
    attempt = 0
    
    overall_result = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "attempts": [],
        "final_status": "Niepowodzenie"
    }
    
    while attempt < max_attempts:
        print(f"\nPróba logowania {attempt + 1}/{max_attempts}")
        if login_to_system():
            overall_result["final_status"] = "Sukces"
            print("\nLogowanie udane! Szczegóły zostały zapisane w pliku markdown.")
            print("Sprawdź wygenerowany plik, aby zobaczyć flagę i zawartość tajnej podstrony.")
            break
        
        # Jeśli nie udało się zalogować, poczekaj chwilę i spróbuj ponownie
        attempt += 1
        if attempt < max_attempts:
            wait_time = 5
            print(f"Oczekiwanie {wait_time} sekund przed kolejną próbą...")
            time.sleep(wait_time)  # Poczekaj 5 sekund przed kolejną próbą
    
    if attempt == max_attempts and overall_result["final_status"] == "Niepowodzenie":
        print("\nPrzekroczono maksymalną liczbę prób logowania.")
    
    print(f"\nZakończono wykonanie skryptu. Ostateczny status: {overall_result['final_status']}")
    print("Jeśli logowanie się powiodło, znalezioną flagę zgłoś do centrali: https://c3ntrala.ag3nts.org/")

if __name__ == "__main__":
    main()
