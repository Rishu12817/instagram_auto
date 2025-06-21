CREATE TABLE dim_lookup (
    id SERIAL PRIMARY KEY,
    username TEXT,
    photo_url TEXT,
    caption TEXT,
    posted TEXT,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

