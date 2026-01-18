# Smart Warehouse API

Backendowy system do zarządzania stanami magazynowymi i logistyką produktów. Projekt stworzony w celu nauki architektury systemów opartych o SQL oraz konteneryzację.

## Tech Stack

* **Core:** Python 3.11, FastAPI
* **Database:** PostgreSQL 15 (uruchamiana w Dockerze)
* **ORM:** SQLAlchemy (interakcja z bazą)
* **Validation:** Pydantic (walidacja payloadów wchodzących do API)
* **Infrastructure:** Docker Compose

## Kluczowe Funkcjonalności

1.  **Zarządzanie Produktami (CRUD):** Pełna obsługa kartoteki produktów i kategorii.
2.  **Transakcyjność Ruchów (ACID):**
    * System nie pozwala na ręczną edycję pola "ilość".
    * Zmiana stanu odbywa się tylko poprzez rejestrację ruchu magazynowego (Przyjęcie(IN)/Wydanie(OUT)).
    * Próba wydania towaru poniżej stanu zero kończy się błędem 400 i rollbackiem transakcji.
3.  **Analityka SQL:** Endpoint `/stats` wykorzystuje agregację po stronie bazy danych (zamiast pętli w Pythonie) do szybkiego raportowania wartości magazynu i wykrywania "low stock alerts".

## Jak uruchomić lokalnie?

Wymagany jest jedynie zainstalowany **Docker Desktop**.

**1. Sklonuj repozytorium:**
```bash
git clone [https://github.com/Konrad02/Smart-Warehouse-API.git](https://github.com/Konrad02/Smart-Warehouse-API.git)
cd Smart-Warehouse-API