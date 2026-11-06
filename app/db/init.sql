CREATE TABLE notes (
    id         SERIAL PRIMARY KEY,
    text       TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Тестовые данные: в тестовых средах нет персональных данных
INSERT INTO notes (text) VALUES
    ('Проверить сборку'),
    ('Написать отчёт по курсовой');
