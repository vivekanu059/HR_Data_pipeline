
CREATE DATABASE EnterpriseHR;
GO

USE EnterpriseHR;
GO


CREATE SCHEMA hr_staging;
GO


CREATE TABLE hr_staging.raw_daily_events (
    log_id INT IDENTITY(1,1) PRIMARY KEY, 
    event_id UNIQUEIDENTIFIER NOT NULL,
    event_timestamp DATETIME2 NOT NULL,
    emp_id INT NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    

    new_salary DECIMAL(10,2) NULL,
    new_role VARCHAR(100) NULL,
    new_department VARCHAR(100) NULL,
    
   
    new_hire_details NVARCHAR(MAX) NULL 
);
GO


CREATE TABLE hr_staging.seed_employees (
    emp_id INT PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    department VARCHAR(100),
    role VARCHAR(100),
    salary DECIMAL(10,2),
    hire_date DATE,
    status VARCHAR(20)
);
GO


USE EnterpriseHR;
GO

BULK INSERT hr_staging.seed_employees
FROM 'D:\hr_data_pipeline\data\seed\initial_employees.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2, 
    FIELDTERMINATOR = ',', 
    ROWTERMINATOR = '\n', 
    TABLOCK
);
GO

SELECT * FROM hr_staging.seed_employees;
GO