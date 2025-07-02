CREATE DATABASE SCHOOL_LIFE;
\c SCHOOL_LIFE;

-- TABLE CLASSROOM
CREATE TABLE Classroom (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255)(255)
);

-- TABLE USER
CREATE TABLE "User" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    level VARCHAR(255)
);

-- TABLE EVENT
CREATE TABLE Event (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    category VARCHAR(255),
    attendance VARCHAR(255),
    place VARCHAR(255),
    date_start TIMESTAMP,
    date_end TIMESTAMP
);

-- TABLE TO_BE (relation entre USER et CLASSROOM)
CREATE TABLE To_Be (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES "User"(id) ON DELETE CASCADE,
    classroom_id INT REFERENCES Classroom(id) ON DELETE CASCADE,
    presence BOOLEAN,
    timestamp TIMESTAMP
);

-- TABLE ORGANIZE (relation USER ↔ EVENT)
CREATE TABLE Organize (
    user_id INT REFERENCES "User"(id) ON DELETE CASCADE,
    event_id INT REFERENCES Event(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, event_id)
);

-- TABLE PARTICIPATE (relation USER ↔ EVENT)
CREATE TABLE Participate (
    user_id INT REFERENCES "User"(id) ON DELETE CASCADE,
    event_id INT REFERENCES Event(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, event_id)
);

-- TABLE MENTORING (relation USER ↔ USER)
CREATE TABLE Mentoring (
    id SERIAL PRIMARY KEY,
    mentor_id INT REFERENCES "User"(id) ON DELETE CASCADE,
    sponsored_id INT REFERENCES "User"(id) ON DELETE CASCADE,
    subject VARCHAR(255)(255),
    description TEXT
);
