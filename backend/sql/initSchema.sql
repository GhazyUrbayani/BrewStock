CREATE TABLE IF NOT EXISTS "transactionRecord" (
  "id" SERIAL PRIMARY KEY,
  "skuId" VARCHAR(64) NOT NULL,
  "transactionDate" DATE NOT NULL,
  "demandQuantity" DOUBLE PRECISION NOT NULL,
  "createdAt" TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS "userAccount" (
  "id" SERIAL PRIMARY KEY,
  "email" VARCHAR(255) NOT NULL UNIQUE,
  "passwordHash" VARCHAR(255) NOT NULL,
  "isActive" BOOLEAN NOT NULL DEFAULT TRUE,
  "createdAt" TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS "refreshTokenRecord" (
  "id" SERIAL PRIMARY KEY,
  "tokenId" VARCHAR(128) NOT NULL UNIQUE,
  "tokenHash" VARCHAR(255) NOT NULL UNIQUE,
  "userId" INTEGER NOT NULL REFERENCES "userAccount"("id"),
  "revokedAt" TIMESTAMPTZ,
  "expiresAt" TIMESTAMPTZ NOT NULL,
  "createdAt" TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS "idxTransactionDateSkuId"
  ON "transactionRecord"("transactionDate", "skuId");
