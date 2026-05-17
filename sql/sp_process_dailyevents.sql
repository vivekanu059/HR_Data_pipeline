USE EnterpriseHR;
GO

CREATE OR ALTER PROCEDURE hr_analytics.sp_process_daily_events
AS
BEGIN
    SET NOCOUNT ON;

   
    UPDATE d
    SET d.is_current = 0, 
        d.end_date = CAST(e.event_timestamp AS DATE), 
        d.status = 'Terminated'
    FROM hr_analytics.dim_employee d
    JOIN hr_staging.raw_daily_events e ON d.emp_id = e.emp_id
    WHERE e.event_type = 'TERMINATION' 
      AND d.is_current = 1;

   
    UPDATE d
    SET d.is_current = 0, 
        d.end_date = CAST(e.event_timestamp AS DATE)
    FROM hr_analytics.dim_employee d
    JOIN hr_staging.raw_daily_events e ON d.emp_id = e.emp_id
    WHERE e.event_type IN ('PROMOTION', 'DEPARTMENT_TRANSFER') 
      AND d.is_current = 1;

    
    INSERT INTO hr_analytics.dim_employee 
    (emp_id, first_name, last_name, department, role, salary, status, start_date, end_date, is_current)
    SELECT 
        e.emp_id,
        d.first_name,
        d.last_name,
        COALESCE(e.new_department, d.department), 
        COALESCE(e.new_role, d.role),             
        COALESCE(e.new_salary, d.salary),         
        'Active',
        CAST(e.event_timestamp AS DATE),          
        NULL,                                     
        1                                         
    FROM hr_staging.raw_daily_events e
    JOIN hr_analytics.dim_employee d ON e.emp_id = d.emp_id
    WHERE e.event_type IN ('PROMOTION', 'DEPARTMENT_TRANSFER') 
      AND d.end_date = CAST(e.event_timestamp AS DATE); 

   
    INSERT INTO hr_analytics.dim_employee 
    (emp_id, first_name, last_name, department, role, salary, status, start_date, end_date, is_current)
    SELECT 
        e.emp_id,
        JSON_VALUE(e.new_hire_details, '$.first_name'),
        JSON_VALUE(e.new_hire_details, '$.last_name'),
        JSON_VALUE(e.new_hire_details, '$.department'),
        JSON_VALUE(e.new_hire_details, '$.role'),
        CAST(JSON_VALUE(e.new_hire_details, '$.salary') AS DECIMAL(10,2)),
        'Active',
        CAST(e.event_timestamp AS DATE),
        NULL,
        1
    FROM hr_staging.raw_daily_events e
    WHERE e.event_type = 'HIRE';

  
    TRUNCATE TABLE hr_staging.raw_daily_events;

    PRINT 'Daily events processed successfully.';
END;
GO

SELECT * FROM hr_analytics.dim_employee
ORDER BY emp_id, start_date;

GO
EXEC hr_analytics.sp_process_daily_events;