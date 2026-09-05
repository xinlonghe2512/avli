Release process
===============

Building and publishing is handled by
[`.github/workflows/release.yaml`](.github/workflows/release.yaml),
triggered by a tag push.

## Steps

1. Update version in the following files and commit on `main`:
    - `CHANGELOG.md`
    - `main.go`
    - `install`
    - `install.ps1`

2. Verify file consistency, sign the tag, and push the tag.

    ```sh
    make tag VERSION=0.1.1
    ```

    `make tag` runs `prerelease` first (checks that the version
    appears in CHANGELOG.md, both man pages, install, and install.ps1)
    and pushes the tag if the checks pass.

    Only the tag is pushed; `main` on origin still points to the
    old version, so `/main/install` keeps resolving against existing
    binaries during the publish window.

3. The workflow fires on the tag push and pauses on the `release`
   environment gate. Approve it in the Actions tab to release.

4. After the GitHub release is published, fast-forward `main`:

    ```sh
    git push origin main
    ```

## Testing the workflow

To exercise the workflow without firing a real release:

1. Actions tab -> **Release** -> **Run workflow**.
2. Pick a branch and enter the version currently on that branch
   (the version-consistency check requires the input to match the
   files in the checked-out tree).
3. Approve the `release` environment gate when prompted.
4. Goreleaser runs with `--snapshot --skip=publish`. Only the GitHub release upload is skipped.

Use this to validate the workflow YAML and version-extraction logic.
