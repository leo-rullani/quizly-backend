Hier ist deine **vollständig angepasste README** (inkl. eigener Repo‑URL, klarer .env‑Erklärung und .env.template‑Flow), einfach so in `README.md` übernehmen:

````markdown
# Quizly – Backend (Django & Django REST Framework)

Quizly ist eine Lernplattform, mit der angemeldete Benutzer auf Basis eines YouTube‑Videos automatisch ein Quiz generieren lassen können.  
Das Backend stellt eine REST‑API zur Verfügung, die:

- Benutzerregistrierung und Login via **JWT + HttpOnly Cookies** ermöglicht
- YouTube‑Videos per **yt-dlp** + **FFmpeg** in Audio konvertiert
- Audio mit **Whisper** transkribiert
- Aus dem Transkript mit **Gemini Flash** ein Quiz mit 10 Fragen erzeugt
- Quizzes speichert, auflistet, anzeigt, aktualisiert (PATCH) und löscht

Dieses Repository enthält **nur das Backend**. Das Frontend wird separat bereitgestellt und greift auf diese API zu.

---

## Inhalt

1. [Technologie-Stack](#technologie-stack)  
2. [Features / User Stories](#features--user-stories)  
3. [Voraussetzungen](#voraussetzungen)  
4. [Installation & Setup](#installation--setup)  
5. [Umgebungsvariablen & .env.template](#umgebungsvariablen--envtemplate)  
6. [Datenmodell](#datenmodell)  
7. [API-Übersicht](#api-übersicht)  
8. [Authentifizierung & Cookies](#authentifizierung--cookies)  
9. [Quiz-Pipeline (YouTube → Audio → Transkript → Quiz)](#quiz-pipeline-youtube--audio--transkript--quiz)  
10. [Tests & Coverage](#tests--coverage)  
11. [Deployment-Hinweise](#deployment-hinweise)  
12. [Rechtliches](#rechtliches)

---

## Technologie-Stack

- **Programmiersprache:** Python 3.12  
- **Web-Framework:** Django 5.x  
- **API:** Django REST Framework  
- **Auth:** djangorestframework-simplejwt (JWT in HttpOnly-Cookies, eigene `CookieJWTAuthentication`)  
- **Datenbank:** SQLite (für Entwicklung; kann leicht gegen PostgreSQL o. Ä. getauscht werden)  
- **YouTube Download:** yt-dlp  
- **Audio/Transcoding:** FFmpeg (Systemabhängige Installation, global verfügbar)  
- **Transkription:** Whisper (lokal, Python-Bibliothek `whisper`)  
- **Quiz-Generierung:** Gemini Flash über das Python-Paket `google-genai`  

---

## Features / User Stories

Diese Implementierung deckt die in der Aufgabenstellung beschriebenen User Stories ab:

- **User Story 1 – Registrierung**  
  - API-Endpoint: `POST /api/register/`  
  - Validiert E-Mail, Passwort & Passwortbestätigung, speichert User  
  - Fehlermeldung bei z. B. bereits verwendeter E-Mail

- **User Story 2 – Login**  
  - API-Endpoint: `POST /api/login/`  
  - Validiert User, erstellt Access- & Refresh-Token und setzt diese als **HttpOnly Cookies**

- **User Story 3 – Logout**  
  - API-Endpoint: `POST /api/logout/`  
  - Löscht/invalidiert Tokens und entfernt Cookies (Token-Blacklist)

- **User Story 4 – Neues Quiz generieren**  
  - API-Endpoint: `POST /api/createQuiz/`  
  - Nimmt YouTube-URL entgegen, verarbeitet Audio & Transkript, erzeugt 10‑Fragen‑Quiz mit 4 Antwortoptionen

- **User Story 5–9 – Quizverwaltung & Spielen**  
  - API-Endpoints:  
    - `GET /api/quizzes/`  
    - `GET /api/quizzes/{id}/`  
    - `PATCH /api/quizzes/{id}/`  
    - `DELETE /api/quizzes/{id}/`  
  - Auflisten, Detailansicht, Aktualisieren (z. B. Titel/Beschreibung), Löschen  
  - Berechtigungen: Nutzer sieht und bearbeitet nur **eigene** Quizzes (403 für fremde Quizzes)

- **User Story 10 – Rechtliches**  
  - Im **Frontend** existieren die Seiten `privacy.html` & `legalnotice.html`  
  - Enthalten Datenschutzerklärung & Impressum (Betreiber: Leugzim Rullani)

---

## Voraussetzungen

Stelle sicher, dass folgende Tools installiert sind:

- **Python 3.12+**
- **Git** (zum Klonen des Repositories)
- **FFmpeg** global installiert

Beispiele FFmpeg:

```bash
# macOS (Homebrew)
brew install ffmpeg

# Ubuntu / Debian
sudo apt-get update
sudo apt-get install ffmpeg

# Windows (Chocolatey)
choco install ffmpeg
````

Alle Python-Abhängigkeiten werden später via `pip` über `requirements.txt` installiert.

---

## Installation & Setup

Die folgenden Schritte sind so beschrieben, dass jemand das Projekt **von Null** aus deinem GitHub-Repository starten kann.

### 1. Repository klonen

```bash
git clone https://github.com/leo-rullani/quizly-backend.git
cd quizly-backend
```

### 2. Virtuelle Umgebung anlegen & aktivieren

```bash
# venv erstellen
python -m venv env

# macOS / Linux
source env/bin/activate

# Windows (PowerShell)
env\Scripts\Activate.ps1
```

### 3. Dependencies installieren

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> Alle benötigten Pakete (z. B. `Django`, `djangorestframework`, `djangorestframework-simplejwt`, `python-dotenv`, `yt-dlp`, `whisper`, `google-genai`, `pytest`, `coverage`) sind in `requirements.txt` enthalten.

### 4. `.env` aus Template erzeugen

Im Projektroot liegt eine Datei **`.env.template`**.
Diese Datei enthält Beispielwerte für alle benötigten Umgebungsvariablen.

```bash
# im Projektroot:
cp .env.template .env
```

Anschließend die Datei `.env` öffnen und anpassen (siehe [Umgebungsvariablen & .env.template](#umgebungsvariablen--envtemplate)).

### 5. Datenbank vorbereiten

```bash
python manage.py migrate
```

### 6. Entwicklungsserver starten

```bash
python manage.py runserver
```

Der Server läuft dann unter:

```text
http://127.0.0.1:8000/
```

Das (bereitgestellte) Frontend greift typischerweise über `http://127.0.0.1:8000/api/...` auf die API zu.

---

## Umgebungsvariablen & .env.template

Die Konfiguration erfolgt über eine `.env`‑Datei im Projektroot.
`core/settings.py` lädt diese Datei mit **python‑dotenv** automatisch:

* Datei im Repo: `.env.template`
* Datei **lokal**: `.env` (wird **nicht** committed)

### 1. `.env.template` → `.env`

```bash
cp .env.template .env
```

### 2. Inhalt von `.env.template`

Beispiel (im Repo):

```env
# Django Settings
DJANGO_SECRET_KEY=change_me_to_a_random_long_string
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# Google Gemini API
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional future settings:
# DATABASE_URL=sqlite:///db.sqlite3
```

### 3. `.env` für lokale Entwicklung anpassen

In deiner **lokalen** `.env` sollten z. B. stehen:

```env
DJANGO_SECRET_KEY=irgendein_langer_geheimer_random_string
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

GOOGLE_API_KEY=DEIN_ECHTER_GEMINI_API_KEY
```

* `DJANGO_SECRET_KEY`
  Wird als `SECRET_KEY` in Django verwendet (in `settings.py` per `os.getenv` geladen).
* `DJANGO_DEBUG`
  `"True"` oder `"False"`. Für lokale Entwicklung typischerweise `True`.
* `DJANGO_ALLOWED_HOSTS`
  Kommagetrennte Liste, z. B. `127.0.0.1,localhost`
* `GOOGLE_API_KEY`
  Dein Gemini‑API‑Key (wird in `quiz_app/utils/gemini_client.py` verwendet).

Die Prüfer:innen können also:

```bash
cp .env.template .env
# dann .env öffnen und Werte eintragen
python manage.py migrate
python manage.py runserver
```

und das Projekt ohne zusätzliche Anpassungen starten.

---

## Datenmodell

### `Quiz`

* `user` – ForeignKey zum User (Owner des Quiz)
* `title` – Titel des Quizzes
* `description` – kurze Beschreibung
* `video_url` – YouTube‑URL, die für das Quiz verwendet wurde
* `created_at` / `updated_at` – Zeitstempel

### `Question`

* `quiz` – ForeignKey auf das zugehörige Quiz
* `question_title` – Fragetext
* `question_options` – JSON-Feld (Liste mit 4 Antwortoptionen)
* `answer` – korrekte Antwort (String, muss einer Option entsprechen)
* `created_at` / `updated_at` – Zeitstempel

---

## API-Übersicht

### Authentication

#### `POST /api/register/`

Registriert einen neuen Benutzer.

**Request Body**

```json
{
  "username": "your_username",
  "password": "your_password",
  "confirmed_password": "your_confirmed_password",
  "email": "your_email@example.com"
}
```

**Response 201**

```json
{
  "detail": "User created successfully!"
}
```

---

#### `POST /api/login/`

Meldet einen Benutzer an und setzt `access_token` und `refresh_token` als **HttpOnly Cookies**.

**Request Body**

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response 200**

```json
{
  "detail": "Login successfully!",
  "user": {
    "id": 1,
    "username": "your_username",
    "email": "your_email@example.com"
  }
}
```

---

#### `POST /api/logout/`

Loggt den Benutzer aus, invalidiert Tokens und entfernt Cookies.

**Response 200**

```json
{
  "detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."
}
```

---

#### `POST /api/token/refresh/`

Erneuert den Access Token per `refresh_token` Cookie.

**Response 200**

```json
{
  "detail": "Token refreshed",
  "access": "new_access_token"
}
```

---

### Quiz Management

#### `POST /api/createQuiz/`

Erstellt ein neues Quiz aus einer YouTube-URL.

**Request Body**

```json
{
  "url": "https://www.youtube.com/watch?v=example"
}
```

**Response 201**

```json
{
  "id": 1,
  "title": "Quiz Title",
  "description": "Quiz Description",
  "created_at": "...",
  "updated_at": "...",
  "video_url": "https://www.youtube.com/watch?v=example",
  "questions": [
    {
      "id": 1,
      "question_title": "Question 1",
      "question_options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "Option A"
    }
  ]
}
```

---

#### `GET /api/quizzes/`

Gibt alle Quizzes des aktuell eingeloggten Benutzers zurück.

**Response 200** (Beispiel)

```json
[
  {
    "id": 1,
    "title": "Quiz Title",
    "description": "Quiz Description",
    "created_at": "...",
    "updated_at": "...",
    "video_url": "https://www.youtube.com/watch?v=example",
    "questions": [
      {
        "id": 1,
        "question_title": "Question 1",
        "question_options": ["Option A", "Option B", "Option C", "Option D"],
        "answer": "Option A"
      }
    ]
  }
]
```

---

#### `GET /api/quizzes/{id}/`

Gibt ein spezifisches Quiz (nur, wenn es dem eingeloggten User gehört) zurück.

---

#### `PATCH /api/quizzes/{id}/`

Partielle Aktualisierung eines Quizzes (z. B. Titel/Description).

Beispiel:

```json
{
  "title": "Partially Updated Title"
}
```

---

#### `DELETE /api/quizzes/{id}/`

Löscht ein Quiz inkl. aller zugehörigen Fragen.

**Response 204** – Kein Body.

---

## Authentifizierung & Cookies

* Nach erfolgreichem Login werden zwei **HttpOnly Cookies** gesetzt:

  * `access_token` (kurze Lebensdauer)
  * `refresh_token` (längere Lebensdauer)

* Das Backend nutzt eine eigene Auth-Klasse
  `auth_app.authentication.CookieJWTAuthentication`,
  die auf **SimpleJWT** basiert und Tokens aus den HttpOnly‑Cookies liest.

* Geschützte Endpunkte (`/api/createQuiz/`, `/api/quizzes/...`) erfordern eine gültige Authentifizierung; sonst gibt es `401 Unauthorized` oder `403 Forbidden`.

---

## Quiz-Pipeline (YouTube → Audio → Transkript → Quiz)

Die Funktionalität zum Erstellen eines Quizzes aus einer YouTube-URL läuft in etwa so ab:

1. **YouTube-URL parsen**

   * Extrahieren der Video-ID
   * Erzeugen einer kanonischen URL

2. **Audio herunterladen**

   * yt-dlp lädt nur die Audio-Spur in ein temporäres Verzeichnis

3. **Transkription**

   * Whisper lädt ein Model (z. B. `"tiny"`)
   * Das Audio-File wird transkribiert → reiner Text

4. **Quiz-Generierung via Gemini**

   * Der Transkript-Text wird mit einem strikten Prompt an **Gemini Flash** gesendet
   * Gemini generiert:

     * Titel
     * Beschreibung (max. 150 Zeichen)
     * exakt 10 Fragen mit jeweils 4 Antwortoptionen und einer richtigen Antwort
   * Das Ergebnis wird in `Quiz` + `Question` Objekte umgewandelt, in der Datenbank gespeichert und an den Client zurückgegeben.

---

## Tests & Coverage

### Django Tests

Die wichtigsten API-Funktionen werden über Django/DRF-Tests (`APITestCase`) abgedeckt, u. a.:

* Registrierung (`/api/register/`)
* Login/Logout/Token Refresh
* `createQuiz` Endpunkt
* Zugriff auf eigene / fremde Quizzes (Status 200 / 401 / 403 / 404)
* PATCH- und DELETE-Szenarien

Ausführen:

```bash
python manage.py test
```

### Pytest & Coverage

Zusätzlich sind `pytest` und `coverage.py` integriert.

```bash
# Tests mit pytest ausführen
pytest

# Coverage messen
coverage run -m pytest
coverage report -m

# Optional: HTML-Report generieren
coverage html
# → öffne htmlcov/index.html im Browser
```

Die aktuelle Testabdeckung liegt bei **> 80 %** (siehe `coverage report -m`).

---

## Deployment-Hinweise

Der integrierte Django-Server (`runserver`) ist **nur für Entwicklung** gedacht.

Für Produktion wird empfohlen:

* WSGI/ASGI-Server verwenden (z. B. gunicorn, uvicorn/daphne)
* `DJANGO_DEBUG=False` setzen
* Sichere Datenbank (z. B. PostgreSQL)
* HTTPS (TLS) verwenden
* Sichere Cookie-Konfiguration (`Secure`, `SameSite`, Domain etc.)
* Eigene `ALLOWED_HOSTS` per `DJANGO_ALLOWED_HOSTS` setzen

---

## Rechtliches

* Betreiber der Anwendung (Frontend/Impressum):
  **Leugzim Rullani**
  Untere Farnbühlstrasse 3
  5610 Wohlen
  E-Mail: `leugzimrullani@outlook.com`

* Detaillierte rechtliche Informationen (Datenschutzerklärung & Impressum) befinden sich im **Frontend** auf:

  * `privacy.html`
  * `legalnotice.html`

```