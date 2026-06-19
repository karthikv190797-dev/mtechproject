# mtechproject

This repository now contains the full "Mtech_project" under `Working_project/Mtech_project`.

Notes:
- The nested repository metadata that previously existed inside `Working_project/Mtech_project` was backed up to `.git.backup` directories and committed. These backups were included so the nested history is preserved locally, but you may want to remove them from the repository to avoid large blob uploads.
- If you prefer `Working_project/Mtech_project` to be a proper submodule instead, remove the included files and add it with:

	git submodule add <url> Working_project/Mtech_project

- Recommended cleanup to remove the `.git.backup` directories from the repo (if desired): add the patterns to `.gitignore`, delete the backup folders, commit, and push.

If you want, I can convert the nested project to a submodule and/or remove the `.git.backup` directories for you.