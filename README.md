# Doit

# placeholder

# placeholder

# Entity relationship diagram - 
ERD subject to change as features and functionality change throughout the development process

```mermaid
erDiagram

    USER ||--o{ TASK : creates
    USER ||--o{ NOTE : writes
    USER ||--o{ FOCUSITEM : manages

    USER {
        int id PK
        string username
        string email
        string password
    }

    TASK {
        int id PK
        int user_id FK
        string title
        text description
        datetime created_at
        datetime updated_at
        datetime due_date
        boolean is_completed
    }

    NOTE {
        int id PK
        int user_id FK
        text content
        datetime created_at
        datetime updated_at
    }

    FOCUSITEM {
        int id PK
        int user_id FK
        string title
        datetime created_at
        datetime updated_at
    }