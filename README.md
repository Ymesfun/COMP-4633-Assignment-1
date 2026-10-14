# COMP-4633-Assignment-1

[add description]

## Setup

```bash
python -m pip install -r requirements.txt
cp .env.example .env
```

The database address is not in the source. Put it in `.env`, which is gitignored:

```
[DB_INFO]=[DB_ADDRESS]
```

## Commands

[describe api commands]

```bash
[call api with python]
```

[describe api call to get request]

```bash
[code input]
```

Add a [database item]. A new UUID is sent as the `Idempotency-Key` header:

```bash
[call add request]
```
