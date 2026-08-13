# VolunteerConnect System Architecture

## UML Class Diagram

```text
+----------------------+
|        User          |
+----------------------+
| id                   |
| name                 |
| email                |
| password             |
| role                 |
+----------------------+
          |
          | creates
          | 1
          v
+----------------------+
|        Event         |
+----------------------+
| id                   |
| title                |
| description          |
| date                 |
| time                 |
| location             |
| capacity             |
| created_by           |
+----------------------+
          ^
          |
          | registered for
          |
+----------------------+
|    Registration      |
+----------------------+
| id                   |
| user_id              |
| event_id             |
| registered_at        |
+----------------------+
          ^
          |
          | belongs to
          |
+----------------------+
|        User          |
+----------------------+
