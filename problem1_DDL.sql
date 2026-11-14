
DROP DATABASE IF EXISTS company;
CREATE DATABASE company;
USE company;

-- 1. DEPARTMENT
CREATE TABLE DEPARTMENT (
    Dnumber INT PRIMARY KEY,
    Dname VARCHAR(50) NOT NULL,
    mgr_ssn INT,
    mgr_start_date DATE
);

-- 2. EMPLOYEE
CREATE TABLE EMPLOYEE (
    ssn INT PRIMARY KEY,
    fname VARCHAR(30) NOT NULL,
    lname VARCHAR(30) NOT NULL,
    bdate DATE,
    address VARCHAR(100),
    gender CHAR(1),
    salary DECIMAL(10, 2),
    super_ssn INT,
    Dno INT,

    FOREIGN KEY (Dno) REFERENCES DEPARTMENT(Dnumber),
    FOREIGN KEY (super_ssn) REFERENCES EMPLOYEE(ssn)
);

-- Add manager foreign key after EMPLOYEE exists
ALTER TABLE DEPARTMENT
ADD FOREIGN KEY (mgr_ssn) REFERENCES EMPLOYEE(ssn);

-- 3. PROJECT
CREATE TABLE PROJECT (
    Pnumber INT PRIMARY KEY,
    Pname VARCHAR(50) NOT NULL,
    Plocation VARCHAR(50),
    Dno INT,

    FOREIGN KEY (Dno) REFERENCES DEPARTMENT(Dnumber)
);

-- 4. WORKS_ON
CREATE TABLE WORKS_ON (
    essn INT,
    Pno INT,
    hours DECIMAL(4, 1),

    PRIMARY KEY (essn, Pno),
    FOREIGN KEY (essn) REFERENCES EMPLOYEE(ssn),
    FOREIGN KEY (Pno) REFERENCES PROJECT(Pnumber)
);

-- 5. DEPENDENT
CREATE TABLE DEPENDENT (
    essn INT,
    dependent_name VARCHAR(50),
    gender CHAR(1),
    bdate DATE,
    relationship VARCHAR(25),

    PRIMARY KEY (essn, dependent_name),
    FOREIGN KEY (essn) REFERENCES EMPLOYEE(ssn)
);
