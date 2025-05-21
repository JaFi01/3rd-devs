# Automatyzacja logowania do systemu robotów (CTF)

Ten projekt zawiera skrypty do automatyzacji logowania do systemu robotów na stronie https://xyz.ag3nts.org/ z wykorzystaniem:
- Danych dostępowych (login: tester, hasło: 574e112a)
- Automatycznego rozwiązywania pytań weryfikacyjnych ze strony
- Generowania raportów w formacie Markdown z wynikami operacji
- Odnajdywania tajnej podstrony i flagi CTF

## Zawartość projektu

- `main.py` - główny skrypt wykorzystujący API OpenAI do odpowiadania na pytania
- `main_alternative.py` - alternatywna wersja używająca predefiniowanego słownika odpowiedzi (nie wymaga API)
- Generowane pliki `login_result_*.md` - raporty z wynikami logowania

## Wymagania

- Python 3.7 lub nowszy
- Biblioteki:
  - requests
  - beautifulsoup4
  - openai (tylko dla `main.py`)
  - python-dotenv (tylko dla `main.py`)

## Instalacja

Zainstaluj wymagane biblioteki:

```bash
pip install requests beautifulsoup4 openai python-dotenv
```

Dla wersji z OpenAI API, utwórz plik `.env` zawierający twój klucz API:
```
OPENAI_API_KEY=twój_klucz_api_openai
```

## Użycie

### Wersja z OpenAI API (main.py)

1. Upewnij się, że masz poprawnie skonfigurowany plik `.env` z kluczem API
2. Uruchom skrypt:
   ```bash
   python main.py
   ```
3. Skrypt spróbuje automatycznie zalogować się do systemu i utworzy plik `login_result_*.md` z wynikami

### Wersja alternatywna (main_alternative.py)

1. Uruchom skrypt:
   ```bash
   python main_alternative.py
   ```
2. Ta wersja wykorzystuje predefiniowany słownik odpowiedzi i nie wymaga klucza API
3. Również generuje plik `login_result_alt_*.md` z wynikami

## Jak to działa

1. Skrypt pobiera stronę logowania
2. Wyciąga pytanie weryfikacyjne z HTML
3. Uzyskuje odpowiedź na pytanie (przez API OpenAI lub z lokalnego słownika)
4. Wysyła dane logowania wraz z odpowiedzią poprzez POST request
5. Sprawdza czy otrzymano przekierowanie do tajnej podstrony
6. Odwiedza tajną podstronę i wyszukuje flagę
7. Generuje szczegółowy raport w formacie Markdown

## Format pliku wynikowego

Każda próba logowania generuje plik Markdown zawierający:

- Informacje podstawowe (czas, URL, login)
- Pytanie pobrane ze strony
- Odpowiedź wygenerowaną przez LLM lub słownik
- Status logowania (sukces/niepowodzenie)
- URL tajnej podstrony (jeśli logowanie się powiodło)
- Znalezioną flagę (w formacie flag{...})
- Pełną odpowiedź z tajnej podstrony lub serwera logowania
- Informacje o ewentualnych błędach

## Uwagi

- Skrypt próbuje logować się kilkukrotnie w przypadku niepowodzenia
- W przypadku wersji z lokalnym słownikiem, ograniczona jest liczba pytań, na które skrypt może odpowiedzieć
- Wersja z OpenAI wymaga działającego połączenia internetowego i klucza API
- Po znalezieniu flagi, należy ją zgłosić do centrali: https://c3ntrala.ag3nts.org/
