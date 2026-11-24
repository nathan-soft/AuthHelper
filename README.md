# Auth Helper

A lightweight, configurable command-line authentication tool for interacting with APIs that require username/password authentication and return access tokens.

Auth Helper allows you to authenticate against multiple APIs using configurable profiles, automatically manage access-token caching, and retrieve tokens when needed — without repeatedly performing the login process.

Instead of writing a separate authentication script for every API, configure your API once and use Auth Helper to manage authentication for you.

---

## Features

- **Multiple authentication profiles** – Manage authentication credentials for multiple APIs from a single CLI tool.
- **Configurable login endpoints** – Define the authentication endpoint for each API.
- **Custom request payloads** – Configure the credentials and additional data required by an API.
- **Flexible response mapping** – Extract access tokens and response information from different JSON structures.
- **JWT and API key support** – Authenticate with APIs that return JWTs or ordinary API keys.
- **Automatic token caching** – Cache access tokens and API keys after successful authentication.
- **Token expiration awareness** – Read JWT expiration information to determine whether a cached token is still valid.
- **Cached API key reuse** – Reuse cached API keys when expiration information is unavailable.
- **Profile management** – Create, list, switch, and remove authentication profiles from the CLI.
- **Clipboard support** – Copy an access token directly to the clipboard.
- **Fresh authentication** – Force a new login using the `--fresh` option to bypass a cached token.
- **Centralised error handling** – Display application errors as readable CLI messages instead of exposing raw Python tracebacks.

---

## Downloads

### Windows

<escape> </escape>[**Download Auth Helper for Windows (64-bit)**](https://github.com/nathan-soft/AuthHelper/releases/latest)

Download the latest Windows installer from the GitHub Releases page.

**Installation:**

1. Download `AuthHelperSetup.exe`.
2. Run the installer.
3. Open a new terminal window.
4. Verify the installation:

   ```powershell
   auth --help
   ```

The installer automatically configures the `auth` command and adds it to your user PATH. A separate Python installation is not required.

### Verify download integrity

Each Windows release includes a SHA-256 checksum for the installer.

To verify the downloaded file using PowerShell:

```powershell
Get-FileHash .\AuthHelperSetup.exe -Algorithm SHA256
```

Compare the resulting hash with the SHA-256 value published in the corresponding GitHub Release.

### Other platforms

- Windows: Available
- Linux: Planned
- macOS: Planned

Cross-platform installation options are under development.

---

## Installation

### Windows

Download and run the Auth Helper Windows installer.

The installer automatically:

- Installs Auth Helper.
- Configures the `auth` command.
- Adds the installation directory to your user PATH.
- Allows you to use Auth Helper from PowerShell or Command Prompt without requiring a separate Python installation.

After installation, open a new terminal window.

Verify the installation:

```powershell
auth --help
```

### Verify installation

```powershell
auth --help
```

You should see the available commands:

```text
Commands:
  add-profile
  list
  login
  remove-profile
  show
  status
  use
```

---

## Getting Started

### 1. Create an authentication profile

Run:

```bash
auth add-profile
```

Auth Helper will interactively request the information required to configure your API, including:

- Profile name
- Login URL
- Request payload fields
- Token response path
- Error response path
- Success response path

Sensitive payload fields, such as passwords and secrets, are entered using a concealed input prompt where supported.

### 2. View your profiles

```bash
auth list
```

This displays the authentication profiles configured on your machine.

### 3. Authenticate

Use your default profile:

```bash
auth login
```

Or specify a profile:

```bash
auth login staff_api
```

Auth Helper will authenticate against the configured API and retrieve the access token.

### 4. Copy the access token

To copy the access token to your clipboard:

```bash
auth login --copy
```

To force a fresh login instead of using a valid cached token:

```bash
auth login --fresh
```

You can combine both options:

```bash
auth login --fresh --copy
```

### 5. Switch your default profile

```bash
auth use another_api
```

The specified profile becomes the default profile used when a profile is not explicitly supplied.

---

## CLI Commands

| Command | Description |
|---|---|
| `auth login` | Authenticate using the default profile. |
| `auth login PROFILE` | Authenticate using a specified profile. |
| `auth login --copy` | Authenticate and copy the access token to the clipboard. |
| `auth login --fresh` | Force a new authentication request, bypassing a valid cached token. |
| `auth list` | List configured authentication profiles. |
| `auth use PROFILE` | Set a profile as the default profile. |
| `auth show` | Display the current/default profile information. |
| `auth status` | Display authentication status information. |
| `auth add-profile` | Interactively create a new authentication profile. |
| `auth remove-profile` | Remove an authentication profile. |
| `auth remove-profile PROFILE` | Remove a specified profile. |
| `auth --help` | Display CLI help. |

---

## Authentication and Token Caching

Auth Helper automatically caches access tokens obtained through successful authentication.

When you run:

```bash
auth login
```

Auth Helper checks whether a cached access token exists and whether it is still valid.

The way cached tokens are handled depends on the type of token returned by the API:

- **JWT with an expiration claim:** Auth Helper reads the expiration date and reuses the cached token until it expires. Once expired, a new login request is performed.
- **JWT without an expiration claim:** Auth Helper cannot determine when the token expires. The cached token is reused until a fresh login is requested.
- **Ordinary API keys:** Since API keys do not contain JWT expiration information, Auth Helper caches and reuses them without checking an expiration date.

If no cached token exists, Auth Helper performs a new login request using the credentials configured for the selected profile.

To force a new login regardless of whether a cached token exists:

```bash
auth login --fresh
```

This replaces the previously cached token with the newly obtained token.

The token cache is managed automatically and does not normally require manual modification.

**Note:** For tokens without a detectable expiration date, Auth Helper cannot determine whether the API provider has invalidated them. If a cached token stops working, use `--fresh` to obtain a new one.

---

## Configuration & Profiles

Auth Helper supports multiple authentication profiles, allowing you to authenticate against different APIs using a single CLI tool.

Each profile contains:

- **URL** – The API's login endpoint.
- **Payload** – The request body containing credentials and any additional fields required by the API.
- **Response Mapping** – Defines where access-token, success, and error information can be found in the API response.
- **Cache** – Stores the access token and expiry information automatically after a successful login.

### Configuration Location

Auth Helper automatically creates and reads its configuration from your operating system's user configuration directory.

| Operating System | Configuration Location |
|---|---|
| Windows | `%LOCALAPPDATA%\AuthHelper\profiles.json` |
| macOS | `~/Library/Application Support/AuthHelper/profiles.json` |
| Linux | `~/.config/AuthHelper/profiles.json` |

The configuration directory is separate from the application installation directory. Uninstalling Auth Helper does not intentionally remove your user configuration.

### Example Configuration

```json
{
  "default": "my_api",
  "profiles": {
    "my_api": {
      "payload": {
        "username": "YOUR_USERNAME",
        "password": "YOUR_PASSWORD"
      },
      "url": "https://your-api.com/api/auth/login",
      "response_mapping": {
        "token_path": "data.accessToken",
        "error_path": "errors",
        "success_path": "success"
      },
      "cache": {
        "access_token": "",
        "expires_at": ""
      }
    }
  }
}
```

### Profile Fields

| Field | Description |
|---|---|
| `default` | Name of the default profile used when no profile is specified. |
| `profiles` | Collection of authentication profiles. |
| `payload` | Credentials and additional fields sent to the login endpoint. |
| `url` | Login API endpoint. |
| `response_mapping` | Defines the response fields Auth Helper uses to interpret the API response. |
| `token_path` | JSON path to the access token. |
| `error_path` | JSON path to error information. |
| `success_path` | JSON path to the API's success indicator. |
| `cache` | Automatically managed token cache. |
| `access_token` | Cached access token. |
| `expires_at` | Cached token expiration date/time. |

---

## Response Mapping

Response mapping uses dot notation to navigate nested JSON properties.

For example, if your API returns:

```json
{
  "success": true,
  "data": {
    "accessToken": "YOUR_ACCESS_TOKEN"
  },
  "errors": null
}
```

Your token mapping should be:

```json
"token_path": "data.accessToken"
```

If your API returns the token at the root level:

```json
{
  "token": "YOUR_ACCESS_TOKEN"
}
```

Use:

```json
"token_path": "token"
```

Configure the mappings to match the actual response returned by your API.

---

## Multiple Profiles

You can configure multiple APIs under the `profiles` section.

For example:

```json
{
  "default": "staff_api",
  "profiles": {
    "staff_api": {
      "payload": {
        "username": "YOUR_USERNAME",
        "password": "YOUR_PASSWORD"
      },
      "url": "https://api.example.com/staff/login",
      "response_mapping": {
        "token_path": "data.accessToken",
        "error_path": "errors",
        "success_path": "success"
      },
      "cache": {
        "access_token": "",
        "expires_at": ""
      }
    },
    "another_api": {
      "payload": {
        "email": "YOUR_EMAIL",
        "password": "YOUR_PASSWORD"
      },
      "url": "https://another-api.com/login",
      "response_mapping": {
        "token_path": "token",
        "error_path": "error",
        "success_path": "success"
      },
      "cache": {
        "access_token": "",
        "expires_at": ""
      }
    }
  }
}
```

### Use a specific profile

```bash
auth login another_api
```

### Change the default profile

```bash
auth use another_api
```

After changing the default profile, commands that do not explicitly specify a profile will use the selected default.

---

## Profile Management

Auth Helper allows you to manage profiles directly from the CLI without manually editing the configuration file.

### Add a profile

```bash
auth add-profile
```

Follow the prompts to configure the new profile.

### List profiles

```bash
auth list
```

### Change the default profile

```bash
auth use PROFILE_NAME
```

### Remove a profile

```bash
auth remove-profile
```

You can also specify the profile name:

```bash
auth remove-profile PROFILE_NAME
```

Auth Helper asks for confirmation before removing a profile.

The default profile cannot be removed until another profile is selected as the default.

---

## Security

Auth Helper's configuration file contains sensitive information, including:

- API usernames
- Passwords
- API secrets, where configured
- Cached access tokens

Treat your configuration file as sensitive.

**Do not:**

- Commit `profiles.json` to a public repository.
- Share your configuration file.
- Distribute your personal configuration with the application.
- Expose cached access tokens in screenshots, logs, or public messages.
- Store your real credentials in example configuration files.

When sharing configuration examples, replace credentials and tokens with placeholders.

---

## Troubleshooting

### `auth` is not recognized as a command

After installing Auth Helper, open a new terminal window.

If the command is still unavailable, verify that the Auth Helper installation directory is present in your user PATH.

### Authentication fails

Verify:

- The configured login URL is correct.
- The API is accessible.
- The payload contains the required fields.
- The credentials are correct.
- The response mapping matches the API's actual response structure.

### The token is not being extracted

Check your `token_path` configuration.

For a response such as:

```json
{
  "data": {
    "accessToken": "abc123"
  }
}
```

The correct mapping is:

```json
"token_path": "data.accessToken"
```

### A cached token is being reused

Use:

```bash
auth login --fresh
```

This forces a new login request instead of relying on a valid cached token.

---

## Development

Auth Helper is built with Python.

### Requirements

- Python
- pip

### Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/AuthHelper.git
cd AuthHelper
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run during development

```bash
python main.py --help
```

For example:

```bash
python main.py list
python main.py status
python main.py login
```

### Build the Windows executable

Auth Helper uses PyInstaller for packaging.

```bash
pyinstaller --clean --console --onedir --name AuthHelper main.py
```

The packaged application will be generated in:

```text
dist/AuthHelper/
```

### Build the Windows installer

The Windows installer is generated using Inno Setup and the `AuthHelper.iss` installer script.

---

## Roadmap

- [x] Multiple authentication profiles
- [x] Interactive profile creation
- [x] Profile switching
- [x] Profile removal
- [x] Access-token caching
- [x] Token expiration awareness
- [x] Clipboard support
- [x] Standalone Windows executable
- [x] Windows installer
- [ ] GitHub release distribution
- [ ] Simplified installation process
- [ ] Linux distribution
- [ ] macOS distribution
- [ ] Improved documentation and examples

---

## License

License information will be added when the project license is established.
