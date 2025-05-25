Znajdź najkrótszą ścieżkę dla robota na tej mapie:

mapa = [
  ['p', 'X', 'p', 'p', 'p', 'p'], //wiersz 0
  ['p', 'p', 'p', 'X', 'p', 'p'], //wiersz 1  
  ['p', 'X', 'p', 'X', 'p', 'p'], //wiersz 2
  ['O', 'X', 'p', 'p', 'p', 'F']  //wiersz 3
];

GDZIE:
- 'p' = puste pole (można przejść)
- 'X' = ściana (NIE MOŻNA przejść)
- 'O' = pozycja startowa robota (wiersz 3, kolumna 0)
- 'F' = cel do osiągnięcia (wiersz 3, kolumna 5)

REGUŁY:
- Robot może się poruszać tylko: UP, DOWN, LEFT, RIGHT
- Robot nie może wejść na ścianę 'X'
- Robot nie może wyjść poza mapę

PROCES ROZWIĄZANIA:
1. ANALIZA: Określ pozycję startową i docelową
2. PLANOWANIE: Wymyśl trasę unikając ścian
3. WALIDACJA: Sprawdź każdy krok czy nie prowadzi na ścianę
4. WERYFIKACJA: Nałóż trasę na mapę i sprawdź czy jest poprawna
5. OPTYMALIZACJA: Upewnij się że trasa jest najkrótsza

ODPOWIEDŹ:
Pokaż swoje przemyślenia, a następnie umieść finalną odpowiedź w tagach <RESULT>:

- tutaj rozumowanie robota
- kolejna linia rozumowania

<RESULT>
{
  "steps": "UP, RIGHT, DOWN, LEFT"
}
</RESULT>

WAŻNE: Sprawdź dokładnie każdy krok aby robot nigdy nie wszedł na ścianę 'X'!