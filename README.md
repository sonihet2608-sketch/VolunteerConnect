# VolunteerConnect

VolunteerConnect is a small web prototype that connects university students with local community volunteering opportunities. Students can browse and register for events, while charity users can create volunteer events.

## Team

## Team

- Het Soni — Frontend, Backend, Security Audit and Social Responsibility

## 1. Problem

Students may want to volunteer but have difficulty discovering simple, local opportunities and registering for them. Small community organisations also need a straightforward way to advertise volunteer activities.

## 2. Solution

VolunteerConnect provides a focused portal with three core screens:

1. Login
2. Volunteer Dashboard
3. Event Details

Student users browse upcoming opportunities and register. Charity users can create events from the dashboard.

## 3. Scope Control

The prototype deliberately follows the RFP constraints:

- Maximum 3 core screens: **3**
- Maximum 3 database entities: **3**
- AI-assisted code is manually reviewed before inclusion.

### Database entities

- `users`
- `events`
- `registrations`

## 4. Technology Stack

- Python
- Flask
- SQLite
- HTML/CSS
- Git/GitHub
- Generative AI used as a development assistant

## 5. System Architecture

The system follows a simple client-server architecture:

```text
+------------------+
|   Web Browser    |
| HTML / CSS       |
+--------+---------+
         |
         v
+------------------+
|   Flask App      |
| Routes + Auth    |
| Validation       |
+--------+---------+
         |
         v
+------------------+
|     SQLite       |
| Users            |
| Events           |
| Registrations    |
+------------------+
```

See `docs/system_architecture.png` for the UML-style component/class view.

## 6. Database Relationships

```text
Users (1) --------< Events
  |                  |
  |                  |
  +------< Registrations >------+
             ^
             |
           Events
```

- A charity user can create many events.
- A student can have many registrations.
- An event can have many registrations.
- A unique constraint prevents the same student registering for the same event more than once.

## 7. Running the Application

### Requirements

Python 3.10+ is recommended.

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start the application

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

### Demo accounts

Student:

```text
Email: het@student.example
Password: Student123!
```

Charity:

```text
Email: charity@volunteerconnect.example
Password: Charity123!
```

These are demonstration accounts only and must not be used for real personal information.

## 8. AI-Assisted Development and Manual Review

Generative AI was used to assist with code generation, explanation and debugging. The team remained responsible for the final architecture, security and ethical decisions.

Our review process was:

1. Generate or discuss a code solution with AI.
2. Inspect the generated code manually.
3. Check authentication, input handling and database queries.
4. Test the behaviour.
5. Correct identified problems.
6. Commit only reviewed code.

AI output was therefore treated as a draft rather than trusted production code.

## 9. Security Audit — OWASP SQL Injection

### Risk

SQL Injection can occur when untrusted user input is directly concatenated into SQL statements.

An unsafe pattern would be:

```python
query = "SELECT * FROM users WHERE email='" + email + "'"
```

This was not used in the final authentication implementation.

### Mitigation

The application uses parameterised SQL:

```python
conn.execute(
    "SELECT id, name, email, password, role FROM users WHERE email = ?",
    (email,)
)
```

The value is supplied separately from the SQL command, so user input is treated as data rather than SQL syntax.

### Manual audit result

| Security check | Result |
|---|---|
| Parameterised user lookup | PASS |
| Parameterised event lookup | PASS |
| Parameterised registration insert | PASS |
| Parameterised event creation | PASS |
| Password hashing | PASS |
| Empty input validation | PASS |
| Role-based access checks | PASS |
| Duplicate registration prevention | PASS |

### SQL Injection test

The login form was tested with an input pattern such as:

```text
' OR '1'='1
```

The application does not bypass authentication because the input is handled as a parameter value.

## 10. Additional Security Controls

### Passwords

Passwords are stored using Werkzeug password hashing rather than plain text.

### Role checks

Only authenticated charity users can create events.

Only authenticated student users can register.

### Input validation

Required fields and length/capacity limits are applied to event creation.

### Database constraints

Foreign keys and a unique registration constraint reduce invalid and duplicate data.

## 11. Testing

The project includes tests for:

- Successful login
- Invalid login
- Student registration
- Duplicate registration
- Charity event creation

Run:

```bash
pytest
```

## 12. Social Responsibility Statement

VolunteerConnect is designed around data minimisation and responsible use of user information.

The prototype only requires information needed to operate the service: name, email, authentication information, role and event registration information.

The system does not intentionally:

- sell user information;
- use unnecessary tracking;
- collect precise location data;
- create advertising profiles;
- expose passwords;
- use personal information for unrelated purposes.

Users should be informed about how their information is used, and access to functions is restricted according to role.

## 13. ACM Code of Ethics Alignment

The project aligns with relevant ACM principles:

### Avoid harm

The system is designed to avoid unnecessary collection and exposure of personal information.

### Be honest and trustworthy

The application does not claim that every listed charity or event has been independently verified. It is a prototype for demonstrating the proposed system.

### Respect privacy

Only information necessary for authentication and registration is retained in the prototype.

### Maintain professional competence

The team manually reviews AI-generated code and performs security and functional testing rather than blindly accepting AI output.

### Contribute to society and human well-being

The system aims to make community volunteering easier to discover and access.

## 14. Limitations

This is a prototype rather than a production deployment. It does not currently include email notifications, advanced charity verification, password reset, administrator moderation, cloud hosting or enterprise-scale database infrastructure.

These features were deliberately excluded to respect the RFP's scope-control requirement.

## 15. Future Improvements

Possible future improvements include:

- verified charity accounts;
- email registration confirmations;
- event search/filtering;
- administrator moderation;
- stronger production secret management;
- deployment using a managed database.

These are outside the current prototype scope.

## 16. Team Contribution

### Het Soni

- Frontend implementation
- Backend implementation
- User interface styling
- SQLite database
- Authentication logic
- Event and registration functionality
- Security review
- SQL Injection audit
- Functional testing
- Social responsibility and ACM ethics documentation
- README documentation

## 17. Important Academic Integrity Note

Generative AI was used as a development assistant. The final code and documentation must be reviewed and understood by the team before submission. GitHub commit history should accurately reflect each person's real contribution. No artificial or misleading commits should be created.
