# File Integrity Monitor (HIDS)

## Opis projektu
Projekt implementuje system monitorowania integralności plików (Host-based Intrusion Detection System - HIDS) działający w czasie rzeczywistym. Narzędzie wykrywa nieautoryzowane modyfikacje lub usunięcia plików w zdefiniowanym katalogu i automatycznie przywraca ich pierwotną wersję na podstawie wcześniej przygotowanych wzorców.

System wykorzystuje algorytm SHA-256 do weryfikacji sum kontrolnych oraz bibliotekę watchdog do asynchronicznego monitorowania zdarzeń systemowych.

### Kontekst akademicki
Projekt został przygotowany jako praca zaliczeniowa z przedmiotów:
* Systemy Operacyjne 2 (zarządzanie usługami systemd, procesy w tle, operacje na systemie plików).
* Automatyzacja procesów w inżynierii oprogramowania (automatyzacja wdrażania za pomocą skryptów Bash, mechanizmy samonaprawy systemu).

---

## Struktura plików
Aby skrypt instalacyjny działał poprawnie, pliki w repozytorium muszą być ułożone w następujący sposób:
* src/main.py: Główna logika monitorująca i obsługa zdarzeń.
* src/integrity.py: Moduł odpowiedzialny za obliczanie skrótów kryptograficznych.
* backups/test.txt: Domyślny plik wzorcowy wgrywany podczas instalacji. 
* deploy_hids.yml: Playnook Ansible automatyzujący  pełne wdrożenie.
* inventory.ini: Plik definiujący adresy IP i nazwy użytkownika.
* .gitignore: Konfiguracja wykluczeń dla systemu kontroli wersji.

---

## Instalacja i konfiguracja

### Wymagania wstępne
* Zainstalowany Ansible na maszynie zarządzającej.
* Skonfigurowany serwer SMTP (W moim przypadku była to strona Mailtrap.io).
* System operacyjny Linux na maszynie docelowej z zainstalowanym Pythonem.
* Za pierwszym razem usługa SSH na maszynie docelowej musi zostać ręcznie uruchomiona (jeśli nie była uruchomiona wczesniej).

### Konfiguracja przed uruchomieniem
* W pliku src/main.py uzupełnij dane dostępowe SMTP (Host, Port, User, Password) pobrane z serwera SMTP.
* W pliku inventory.ini wpisz adresy IP maszyn docelowych oraz nazwy użytkownika. 

### Proces automatycznego wdrożenia
Z poziomu maszyny zarządazającej wykonaj komende 
   ansible-playbook -i inventory.ini deploy_hids.yml -kK
Flagi -kK są wymagane tylko przy pierwszym uruchomieni w celu przesłania kluczy SSH i konfiguracji sudo. 
Kolejne wdrożenia odbywaja sie bezhasłowo. 

Po zakończeniu instalacji system zostanie zarejestrowany jako usługa systemd o nazwie file-monitor.service.

### Playbook automatycznie wykonuje następujące czynności
* Konfiguruje usługe SSH, aby uruchamiała się autoamtycznie po restarcie.
* Konfiguruje dostęp bezhasłowy (SSH Keys i Sudoers).
* Instaluje niezbędne pakiety Python (python3-pip, watchdog).
* Wdraża niezbędne pliki konfiugracyjne.
* Rejstruje i uruchamia usługe file-monitor.service.

---

## Procedura dodawania plików do monitorowania
Aby system objął ochroną nowy plik, należy przeprowadzić procedurę synchronizacji:

1. Przygotowanie wzorca:
   sudo cp /sciezka/do/pliku /opt/my_monitor/backups/
2. Inicjalizacja pliku roboczego:
   sudo cp /opt/my_monitor/backups/nazwa_pliku /opt/my_monitor/target_dir/
3. Aktualizacja rejestru haszy:
   sudo systemctl restart file-monitor.service
   
---

## Bezpieczeństwo i odpowiedzialność
Uwaga: Narzędzie to jest prototypem o charakterze edukacyjnym (Proof of Concept). Nie zaleca się używania go w środowiskach produkcyjnych bez dodatkowych zabezpieczeń, takich jak szyfrowanie katalogu wzorców czy ograniczenie uprawnień do plików wykonywalnych.
