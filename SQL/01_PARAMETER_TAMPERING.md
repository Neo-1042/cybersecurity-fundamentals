# Parameter Tampering with PL/SQL

Parameter Tampering is a type of security vulnerability
where a malicious user **manipulates parameters** sent
from a client (UI, URL, API request, input form, JSON)
to the server-side logic, including PL/SQL FUNCTIONS or
PROCEDURES.

Attackers might modify the following parameters:

- IDs (employee_id, customer_id)
- Flags (is_admin, price, has_discount)
- JSON fields
- Hidden input fields
- Query-string values in APEX apps

[+] PL/SQL often powers:

- Oracle APEX apps
- REST Data Services (ORDS)
- Custom backend APIs
- **Enterprise apps where PL/SQL controls business logic**

Because PL/SQL often runs with powerful database privileges,
**parameter tampering** can lead to:

\* Unauthorized data access  
\* Data modification  
\* Escalation of privileges  
\* Bypassing business rules  

# update_salary PL/SQL example

```sql
PROCEDURE update_salary (
    p_emp_id    IN NUMBER,
    p_amount    IN NUMBER
)
IS
BEGIN
    UPDATE employees
    SET salary = p_amount
    WHERE employee_id = p_emp_id;
END;
/
```

If the frontend sends:
```json
    "p_emp_id" : 101,
    "p_amount" : 5000
```
an attacker could tamper the request to:
```json
    "p_emp_id" : 1,
    "p_amount" : 999999
```
if the PL/SQL code does NOT:
- Check the user's authorization level
- Limit the allowed salary range
- Validate that they can modify employee_id = 1

# How to Protect PL/SQL Code from Parameter Tampering?

1. Validate inputs:
```sql
IF p_amount < 0 OR p_amount > 20000 THEN
    RAISE_APPLICATION_ERROR(-20001, 'Invalid salary amount'.);
END IF;
```

2. Never trust client logic

3. Use **Definer's vs Invoker's** Rights Properly

- Definer's rights procedures run with the **schema's privileges**  
- Invoker's rights run with the caller's privileges.

Using invoker's rights (AUTHID CURRENT_USER) reduces risk in
multi-tenant or multi-user systems.

4. Implement Authorization Checks

```sql
IF NOT security_pkg.can_update_emp(v_current_user, p_emp_id) THEN
    RAISE_APPLICATION_ERROR(-20002, 'Unauthorized');
END IF;
```

5. Use Strong Database Constraints

- Foreign Keys
- CHECK constraints
- Row-level security (Fine-Grained Access Control / VPD)

6. Use Bind Variables to Prevent SQL Injection

Not exactly the same as parameter tampering, but often
related. PL/SQL naturally uses bind variables, but when
writing SQL, one must be careful:

```sql
-- Bind variable :id
EXECUTE IMMEDIATE 'SELECT ... WHERE id = :id' USING p_id;
```

**Never concatenate** unchecked values
**inside dynamic SQL**. 

## Safe PL/SQL with Best Practices

```sql
-- %TYPE ---> Anchored Data Type
-- %TYPE tells Oracle:
-- "Use the exact same data type as the employee_id column
-- in the employees table"
CREATE OR REPLACE PROCEDURE secure_update (
    p_emp_id    IN employees.employee_id%TYPE,
    p_amount    IN employees.salary%TYPE,
    p_user_id   IN users.user_id%TYPE
)
IS
BEGIN
    -- 1] Validate input format
    IF p_amount < 0 OR p_amount > 20000 THEN
        RAISE_APPLICATION_ERROR(-20001, 'Invalid amount');
    END IF;

    -- 2] Validate user authorization
    IF NOT security_pkg.can_update(p_user_id, p_emp_id) THEN
        RAISE_APPLICATION_ERROR(-20002, 'Not authorized');
    END IF;

    -- 3] Apply business logic
    UPDATE employees
    SET salary = p_amount
    WHERE employee_id = p_emp_id;

END secure_update;
/
```

## WHERE tbl.clave = P_UNSAFE Example

```sql
-- This SP is UNSAFE
PROCEDURE SP_CONS_S (
    P_CLAVE_X IN NUMBER,
    P_ESTATUS OUT NUMBER
) IS
regexiste NUMBER;
BEGIN
    -- Could leak access to information that the user is not authorized to.
    SELECT COUNT(1) INTO regexiste FROM tbl_emp_s es
    WHERE es.cl_emp = P_CLAVE_X;
END;
/
```

This example is not SQL-injectable (it uses a bind),
but it is **vulnerable to parameter tampering** because
it trusts the client-supplied `P_CLAVE_X` value to decide
what row(s) to read.  
If the caller can change `P_CLAVE_X`, he can probe or learn
about other students or rows.

Let's explore several possible solutions:

## 1] Don't Take Sensitive IDs from the Client (Derive on Server)

**Best fix**:
Don't accept es.cl_emp from the client at all. Derive it
from the authenticated context (APEX session, ORDS/JWT
claims, app user table, etc.)

```sql
CREATE OR REPLACE PROCEDURE get_my_emp_count (
    p_user     IN users.username%TYPE,
    p_count    OUT NUMBER
) 
AUTHID CURRENT_USER
IS
    v_cl_emp tbl_emp_s.cl_emp%TYPE;
BEGIN
    -- FIX: Derive the emp key from server-side identity
    SELECT u.cl_emp
        INTO v_cl_emp
    FROM users u
    WHERE u.username = p_user;

    -- Now, use the server-derived key
    SELECT COUNT(1)
        INTO p_count
    FROM tbl_emp_s es
    WHERE es.cl_emp = v_cl_emp;

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        p_count := 0;
END;
/
```

## 2] Enforce Authorization Before Using the Parameter

If you MUST accept a `cl_emp` argument, gate it through an
authorization check.

```sql
-- PACKAGE ESPECIFICATION
CREATE OR REPLACE PACKAGE security_pkg IS
    FUNCTION can_acces_emp (
        p_user_id IN users.user_id%TYPE,
        p_cl_emp  IN tbl_emp_s.cl_emp%TYPE
    ) RETURN BOOLEAN;
END security_pkg;
/

-- PACKAGE DEFINITION (PACKAGE BODY)

CREATE OR REPLACE PACKAGE BODY security_pkg IS
    FUNCTION can_access_emp (
        p_user_id IN users.user_id%TYPE,
        p_cl_emp  IN tbl_emp_s.cl_emp%TYPE
    ) RETURN BOOLEAN
    IS
        v_dummy NUMBER;
    BEGIN
        -- TO DO
    END;
    /

```