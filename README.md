Ja, lass uns die README fürs Backend bauen.
Hier ist ein kompletter Vorschlag für **`README.md`** für dein Django-Backend. Du kannst ihn 1:1 übernehmen und nur noch ein paar Stellen (Name, Mail, etc.) anpassen.

````markdown
# Quizly – Backend (Django & Django REST Framework)

Quizly ist eine Lernplattform, mit der angemeldete Benutzer auf Basis eines YouTube‑Videos automatisch ein Quiz generieren lassen können.  
Das Backend stellt eine REST‑API zur Verfügung, die:

- Benutzerregistrierung und Login via **JWT + HttpOnly Cookies** ermöglicht
- YouTube‑Videos per **yt-dlp** + **FFmpeg** in Audio konvertiert
- Audio mit **Whisper** transkribiert
- Aus dem Transkript mit **Gemini Flash** ein Quiz mit 10 Fragen erzeugt
- Quizzes speichert, auflistet, anzeigt, updatet und löscht

Dieses Repository enthält **nur das Backend**. Das Frontend wird separat bereitgestellt und greift auf diese API zu.

---

## Inhalt

1. [Technologie-Stack](#technologie-stack)  
2. [Features / User Stories](#features--user-stories)  
3. [Voraussetzungen](#voraussetzungen)  
4. [Installation & Setup](#installation--setup)  
5. [Umgebungsvariablen](#umgebungsvariablen)  
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
- **Auth:** djangorestframework-simplejwt (JWT in HttpOnly-Cookies)  
- **Datenbank:** SQLite (für Entwicklung; kann leicht gegen PostgreSQL o. Ä. getauscht werden)  
- **YouTube Download:** yt-dlp  
- **Audio/Transcoding:** FFmpeg (Systemabhängige Installation, global verfügbar)  
- **Transkription:** Whisper (lokal, Python-Bibliothek `whisper`)  
- **Quiz-Generierung:** Gemini Flash über das Python-Paket `google-genai`  

---

## Features / User Stories

Diese Implementierung deckt die in der Aufgabenstellung beschriebenen User Stories ab:

- **User Story 1 – Registrierung:**  
  - API-Endpoint `/api/register/`  
  - Validiert E-Mail, Passwort & Passwortbestätigung, speichert User

- **User Story 2 – Login:**  
  - API-Endpoint `/api/login/`  
  - Validiert User, erstellt Access- & Refresh-Token und setzt diese als **HttpOnly Cookies**

- **User Story 3 – Logout:**  
  - API-Endpoint `/api/logout/`  
  - Löscht/invalidiert Tokens und entfernt Cookies

- **User Story 4 – Neues Quiz generieren:**  
  - API-Endpoint `/api/createQuiz/`  
  - Nimmt YouTube-URL entgegen, verarbeitet Audio & Transkript, erzeugt 10‑Fragen‑Quiz mit 4 Antwortoptionen

- **User Story 5–9 – Quizverwaltung & Spielen:**  
  - API-Endpoints `/api/quizzes/` & `/api/quizzes/{id}/`  
  - Auflisten, Detailansicht, Aktualisieren (PATCH), Löschen  

- **User Story 10 – Rechtliches:**  
  - Frontend-Seiten `privacy.html` & `legalnotice.html` mit Datenschutzhinweisen und Impressum (vom Frontend genutzt)

---

## Voraussetzungen

Stelle sicher, dass folgende Tools installiert sind:

- **Python 3.12+**
- **FFmpeg** global installiert  
  Beispiele:

  ```bash
  # macOS (Homebrew)
  brew install ffmpeg

  # Ubuntu / Debian
  sudo apt-get update
  sudo apt-get install ffmpeg

  # Windows (Chocolatey)
  choco install ffmpeg
````

* **Git** für das Klonen des Repos

Alle Python-Abhängigkeiten werden später via `pip` installiert.

---

## Installation & Setup

### 1. Repository klonen

```bash
git clone <DEIN-REPOSITORY-URL> quizly-backend
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

> Stelle sicher, dass `djangorestframework`, `djangorestframework-simplejwt`, `yt-dlp`, `whisper`, `google-genai` etc. in deiner `requirements.txt` enthalten sind.

### 4. Umgebungsvariablen setzen

Siehe [Umgebungsvariablen](#umgebungsvariablen).
Für die Entwicklung reicht es oft, die Variablen im Terminal zu exportieren:

```bash
# Beispiel (UNBEDINGT eigenen Secret Key & API Key verwenden!)
export SECRET_KEY="dein_django_secret_key"
export GOOGLE_API_KEY="dein_gemini_api_key"
export DJANGO_DEBUG="1"
```

(Unter Windows entsprechend `set` oder Nutzung einer `.env` / Powershell-Profile.)

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

Das Frontend greift typischerweise über `http://127.0.0.1:8000/api/...` auf die API zu.

---

## Umgebungsvariablen

Mindestens folgende Variablen solltest du setzen:

* `SECRET_KEY`

  * Django Secret Key (niemals committen!)
* `DJANGO_DEBUG`

  * `"1"` oder `"0"` – steuert Debug-Modus
* `GOOGLE_API_KEY`

  * API Key für die Gemini Flash API (wird vom Modul `google-genai` verwendet)

Optional kannst du weitere Einstellungen über Umgebungsvariablen vornehmen (Datenbank, Allowed Hosts etc.).

---

## Datenmodell

### `Quiz`

* `user` – ForeignKey zum User (Owner des Quiz)
* `title` – Titel des Quizzes
* `description` – kurze Beschreibung
* `video_url` – YouTube-URL, die für das Quiz verwendet wurde
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

**Response 200**

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

#### `PATCH /api/quizzes/{id}/`

Partielle Aktualisierung eines Quizzes (z. B. Titel/Description).

Beispiel:

```json
{
  "title": "Partially Updated Title"
}
```

#### `DELETE /api/quizzes/{id}/`

Löscht ein Quiz inkl. aller zugehörigen Fragen.

**Response 204**

Kein Body.

---

## Authentifizierung & Cookies

* Nach erfolgreichem Login werden zwei HttpOnly Cookies gesetzt:

  * `access_token` (kurze Lebensdauer)
  * `refresh_token` (längere Lebensdauer)
* Die Frontend-Requests (z. B. `fetch`, axios, Postman mit „Send cookies“) nutzen diese Cookies automatisch für geschützte Endpunkte (`/api/createQuiz/`, `/api/quizzes/…`).
* Das Backend verwendet `rest_framework_simplejwt.authentication.JWTAuthentication` als Default Auth-Backend.

---

## Quiz-Pipeline (YouTube → Audio → Transkript → Quiz)

Die Funktionalität zum Erstellen eines Quizzes aus einer YouTube-URL läuft in etwa so ab:

1. **YouTube-URL parsen**

   * Extrahiere Video-ID
   * Baue eine kanonische URL

2. **Audio herunterladen**

   * yt-dlp lädt nur die Audio-Spur in ein temporäres Verzeichnis (z. B. `tmp/audio/`)

3. **Transkription**

   * Whisper lädt ein (ggf. gecachtes) Model (z. B. `"tiny"`)
   * Das Audio-File wird transkribiert → reiner Text

4. **Quiz-Generierung**

   * Der Transkript-Text wird mit einem strikten Prompt an Gemini Flash gesendet
   * Gemini generiert:

     * Titel
     * Beschreibung (max. 150 Zeichen)
     * exakt 10 Fragen mit jeweils 4 Antwortoptionen und einer richtigen Antwort
   * Das Ergebnis wird geparst, als `Quiz` + 10 `Question` Objekte in der Datenbank gespeichert und an den Client zurückgegeben.

---

## Tests & Coverage

### Django Tests

Die wichtigsten API-Funktionen werden über Django/DRF-Tests (`APITestCase`) abgedeckt, u. a.:

* Registrierung (`/api/register/`)
* Login/Logout/Token Refresh
* `createQuiz` Endpunkt
* Zugriff auf eigene / fremde Quizzes (200 / 401 / 403 / 404)
* PATCH und DELETE Szenarien

Ausführen der Tests:

```bash
python manage.py test
```

### Pytest & Coverage

Um mindestens **80 % Test Coverage** sicherzustellen, kannst du zusätzlich `pytest` und `coverage.py` verwenden:

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

Stelle sicher, dass `pytest` und `coverage` in deiner `requirements-dev.txt` oder `requirements.txt` enthalten sind.

---

## Deployment-Hinweise

Der integrierte Django-Server (`runserver`) ist **nur für Entwicklung** gedacht.

Für Produktion:

* WSGI/ASGI-Server verwenden (z. B. gunicorn, uvicorn + daphne)
* DEBUG deaktivieren
* Sichere Datenbank (z. B. PostgreSQL)
* HTTPS erzwingen
* Sichere Konfiguration der Cookies (`Secure`, `SameSite`, Domain etc.)

---

## Rechtliches

* Die rechtlichen Informationen (Impressum & Datenschutzerklärung) sind in den Frontend-Seiten:

  * `privacy.html`
  * `legalnotice.html`
* Bitte passe:

  * Betreibername
  * Adresse
  * Kontakt (E-Mail, Telefon)
  * ggf. länderspezifische Anforderungen
    an deine realen Daten an.

---