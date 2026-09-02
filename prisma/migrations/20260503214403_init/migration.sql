-- CreateTable
CREATE TABLE "coffee_logs" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "timestamp" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "caffeine_mg" REAL NOT NULL,
    "coffee_type" TEXT
);

