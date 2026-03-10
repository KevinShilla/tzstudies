# Java Demo (Optional)

This folder is **not** used by the deployed Flask app.
It is here so you can talk about **Java** in interviews without changing Render/Supabase.

## What it does
`FileReport.java` scans the `exams/` folder and prints a quick report:
- subjects found
- levels found (F2, F4, S4, S7, etc.)
- years found
- any filenames it can't parse well

## How to run (locally)
1. Make sure you have Java 17+ (or any modern Java).
2. From the project root, run:

```bash
javac java_demo/FileReport.java
java -cp java_demo FileReport
```

If you want, you can later turn this into a full Spring Boot service.
