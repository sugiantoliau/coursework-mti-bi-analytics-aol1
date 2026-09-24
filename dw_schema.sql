-- ==========================================================
-- DATA WAREHOUSE SCHEMA DDL (POSTGRESQL)
-- ==========================================================

-- 1. DROP EXISTING TABLES (Hapus tabel lama jika ada)
DROP TABLE IF EXISTS "Fact_Returns";
DROP TABLE IF EXISTS "Fact_Order_Detail";
DROP TABLE IF EXISTS "Dim_Order_Header";
DROP TABLE IF EXISTS "Dim_Shipping";
DROP TABLE IF EXISTS "Dim_Customer";
DROP TABLE IF EXISTS "Dim_Product";
DROP TABLE IF EXISTS "Dim_Region";
DROP TABLE IF EXISTS "Dim_Date";

-- ------------------------------------------------------
-- 2. CREATE DIMENSION TABLES
-- ------------------------------------------------------

-- Dim_Date
CREATE TABLE "Dim_Date" (
    "Date ID" INTEGER PRIMARY KEY,
    "Date" DATE,
    "Day" INTEGER,
    "Month" INTEGER,
    "Year" INTEGER
);

-- Dim_Region
CREATE TABLE "Dim_Region" (
    "Region ID" INTEGER PRIMARY KEY,
    "Regional Manager" VARCHAR(255),
    "Region" VARCHAR(50)
);

-- Dim_Product
CREATE TABLE "Dim_Product" (
    "Product ID" VARCHAR(50) PRIMARY KEY,
    "Category" VARCHAR(100),
    "Sub-Category" VARCHAR(100),
    "Product Name" TEXT
);

-- Dim_Customer
CREATE TABLE "Dim_Customer" (
    "Customer ID" VARCHAR(50) PRIMARY KEY,
    "Customer Name" VARCHAR(255),
    "Segment" VARCHAR(50),
    "Country" VARCHAR(100),
    "City" VARCHAR(100),
    "State/Province" VARCHAR(100),
    "Postal Code" VARCHAR(20)
);

-- Dim_Shipping
CREATE TABLE "Dim_Shipping" (
    "Ship ID" INTEGER PRIMARY KEY,
    "Ship Mode" VARCHAR(50)
);

-- Dim_Order_Header
CREATE TABLE "Dim_Order_Header" (
    "Order ID" VARCHAR(50) PRIMARY KEY,
    "Date ID" INTEGER,
    "Order Date" DATE,
    "Ship Date" DATE,
    "Ship ID" INTEGER,
    "Customer ID" VARCHAR(50),
    "Region ID" INTEGER,

    CONSTRAINT fk_order_header_date
        FOREIGN KEY ("Date ID")
        REFERENCES "Dim_Date" ("Date ID"),

    CONSTRAINT fk_order_header_shipping
        FOREIGN KEY ("Ship ID")
        REFERENCES "Dim_Shipping" ("Ship ID"),

    CONSTRAINT fk_order_header_customer
        FOREIGN KEY ("Customer ID")
        REFERENCES "Dim_Customer" ("Customer ID"),

    CONSTRAINT fk_order_header_region
        FOREIGN KEY ("Region ID")
        REFERENCES "Dim_Region" ("Region ID")
);

-- ------------------------------------------------------
-- 3. CREATE FACT TABLES
-- ------------------------------------------------------

-- Fact_Order_Detail
CREATE TABLE "Fact_Order_Detail" (
    "Order ID" VARCHAR(50),
    "Product ID" VARCHAR(50),
    "Sales" NUMERIC(18, 4),
    "Quantity" INTEGER,
    "Discount" NUMERIC(10, 4),
    "Profit" NUMERIC(18, 4),

    CONSTRAINT fk_order_detail_order
        FOREIGN KEY ("Order ID")
        REFERENCES "Dim_Order_Header" ("Order ID"),

    CONSTRAINT fk_order_detail_product
        FOREIGN KEY ("Product ID")
        REFERENCES "Dim_Product" ("Product ID")
);

-- Fact_Returns
CREATE TABLE "Fact_Returns" (
    "Order ID" VARCHAR(50) PRIMARY KEY,
    "Returned" VARCHAR(20),
    "Return_Count" INTEGER,

    CONSTRAINT fk_returns_order
        FOREIGN KEY ("Order ID")
        REFERENCES "Dim_Order_Header" ("Order ID")
);