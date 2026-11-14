
USE company;

-- 1. DEPARTMENTS
-- Department 4 intentionally has no employees.
-- Managers are assigned after inserting employees.

INSERT INTO DEPARTMENT
(Dnumber, Dname, mgr_ssn, mgr_start_date)
VALUES
(1, 'HR', NULL, '2023-01-01'),
(2, 'IT', NULL, '2023-02-01'),
(3, 'Finance', NULL, '2023-03-01'),
(4, 'Marketing', NULL, '2023-04-01');


-- 2. EMPLOYEES
-- Employee 101 has no supervisor.
-- Department 1 has four employees.

INSERT INTO EMPLOYEE
(ssn, fname, lname, bdate, address, gender, salary, super_ssn, Dno)
VALUES
(101, 'John', 'Doe', '1990-05-15', '123 Main St, Houston', 'M', 6000.00, NULL, 1),
(102, 'Jane', 'Smith', '1992-08-20', '456 Oak St, Houston', 'F', 4500.00, 101, 1),
(103, 'Ali', 'Hassan', '1988-11-10', '789 Pine St, Cairo', 'M', 8000.00, 101, 1),
(104, 'Sara', 'Ahmed', '1995-03-12', '12 Palm St, Houston', 'F', 3500.00, 102, 1),
(105, 'Omar', 'Khaled', '1991-07-25', '45 Nile St, Alexandria', 'M', 5500.00, NULL, 2),
(106, 'Mona', 'Ibrahim', '1993-09-18', '67 Garden St, Cairo', 'F', 7000.00, 105, 3);


-- 3. DEPARTMENT MANAGERS

UPDATE DEPARTMENT
SET mgr_ssn = 101
WHERE Dnumber = 1;

UPDATE DEPARTMENT
SET mgr_ssn = 105
WHERE Dnumber = 2;

UPDATE DEPARTMENT
SET mgr_ssn = 106
WHERE Dnumber = 3;


-- 4. PROJECTS
-- Project 40 intentionally has nobody working on it.

INSERT INTO PROJECT
(Pnumber, Pname, Plocation, Dno)
VALUES
(10, 'Web Redesign', 'Cairo', 2),
(20, 'ERP System', 'Alexandria', 3),
(30, 'Recruitment Drive', 'Giza', 1),
(40, 'Mobile Application', 'Cairo', 2);


-- 5. WORKS_ON
-- Employee 101 works on two projects.

INSERT INTO WORKS_ON (essn, Pno, hours)
VALUES
(101, 10, 15.0),
(101, 20, 12.0),
(102, 30, 10.0),
(103, 20, 25.0),
(104, 30, 8.0),
(105, 10, 18.0),
(106, 20, 14.0),
(102, 10, 6.0);


-- 6. DEPENDENTS

INSERT INTO DEPENDENT
(essn, dependent_name, gender, bdate, relationship)
VALUES
(101, 'Adam Doe', 'M', '2015-06-10', 'Son'),
(102, 'Laila Smith', 'F', '2018-02-14', 'Daughter'),
(105, 'Nour Khaled', 'F', '2016-09-21', 'Daughter');
