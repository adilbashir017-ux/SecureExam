# Public Demo Flow

The public demo uses two independent browser credentials:

```text
secureexam_token        -> short-lived JWT for the current logged-in role
secureexam_demo_session -> random token for the browser's private demo sandbox
```

`Logout` / `Switch demo role` removes only `secureexam_token`.

The demo sandbox token remains, so David, Alice and Eve all operate on the same exams and submissions created by that browser.

`Start fresh` requests deletion of the current sandbox and then clears both browser tokens. The next one-click demo login creates a completely new sandbox.

## Database isolation

Two additional tables support isolation:

```text
demo_sessions
- id
- token_hash
- created_at
- expires_at

demo_session_exams
- exam_id
- demo_session_id
- created_at
```

The raw demo token is never stored in MySQL. Only its SHA-256 hash is stored.

Every exam created in a demo sandbox receives a row in `demo_session_exams`. All exam reads, publishes, attempts, submissions, decryptions and security-lab operations enforce that scope from the signed JWT's `demo_session_id`.

Regular non-demo logins can only access exams that are not mapped to a demo session.
