# Private contact context setup

Amrielle can receive a user contact address at runtime without committing it to this public repository.

## One-time setup

1. Open the repository's **Settings** on GitHub.
2. Under **Secrets and variables**, choose **Actions**.
3. Select **New repository secret**.
4. Set the name to `AMRIELLE_CONTACT_EMAIL`.
5. Set the value to the address the user wants Amrielle to know, then save.

The workflow passes this secret to the worker process as an environment variable. The worker injects it into the model's private runtime prompt and redacts exact-address echoes from the model reflection before it can be written to `state.json` or `journal.md`. Do not print the secret or put it in issues, source code, commits, or logs.

## Important boundaries

- The repository is public; **never** put the actual email address in repository files, issues, or pull requests.
- This secret does not itself send email or authorize Amrielle to contact anyone. Separate explicit authorization is required before sending messages.
- If `OPENAI_API_KEY` is configured, the prompt (including the contact address) is sent to the configured OpenAI API. Otherwise, the workflow uses the local Ollama model running in the GitHub Actions job.
- The secret is only available to workflows that GitHub permits to access repository secrets. Forked pull-request workflows do not receive repository secrets.
- Adding the secret does not alter past journals or retroactively update already completed worker runs.
