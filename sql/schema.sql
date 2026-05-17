--- Data coming from the python to the sql server
SELECT * FROM EnterpriseHR.hr_staging.raw_daily_events;


---analytics schema creation
USE EnterpriseHR;
GO


CREATE SCHEMA hr_analytics;
GO

CREATE TABLE hr_analytics.dim_employee (
    emp_sk INT IDENTITY(1,1) PRIMARY KEY, 
    emp_id INT NOT NULL,                  
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    department VARCHAR(100),
    role VARCHAR(100),
    salary DECIMAL(10,2),
    status VARCHAR(20),
    
    
    start_date DATE NOT NULL,
    end_date DATE NULL,                  
    is_current BIT DEFAULT 1             
);
GO


INSERT INTO hr_analytics.dim_employee 
(emp_id, first_name, last_name, department, role, salary, status, start_date, end_date, is_current)
SELECT 
    emp_id, 
    first_name, 
    last_name, 
    department, 
    role, 
    salary, 
    status, 
    hire_date AS start_date, 
    NULL AS end_date,         
    1 AS is_current           
FROM hr_staging.seed_employees;
GO

SELECT * FROM hr_analytics.dim_employee;
GO