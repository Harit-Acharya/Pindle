# PINDLE: FUSE-based Filesystem and Folder Syncer
![screenshot](pindle.tech_hosted/mainicon.png | width=60)

PINDLE is a hybrid file management solution designed to enhance productivity in today's cloud-driven and hybrid work environments. By leveraging FUSE (Filesystem in Userspace), PINDLE integrates multiple cloud storage accounts into a seamless user experience and enables automated syncing between devices.

## Features

- **Cloud Mounter**:
  - Supports mounting Google Drive and OneDrive as local file systems.
  - Easy-to-use GUI for mounting and managing cloud accounts.
  - Automates OAuth authentication and manages tokens for seamless access.
  - Handles file operations such as reading, writing, creating, and deleting directly within the mounted filesystem.

- **Folder Syncer**:
  - Sync folders between devices via cloud storage.
  - GUI-based configuration for mapping folders and managing sync settings.
  - Automated handling of offline-to-online transitions with local caching and conflict resolution.

## Technologies Used

- **FUSE**: For creating user-space filesystems.
- **Python**: Backend implementation and API integration.
- **Cloud APIs**: Google Drive and OneDrive APIs for cloud interactions.
- **Graphical User Interface**: Simplified user interaction for non-technical users.

## Installation

1. Visit the [PINDLE website](https://pindleproject.github.io/pindle.tech/) to download the latest installer for your operating system.
2. Run the installer:
   - **Windows**: Download and run the `.exe` file, then follow the setup wizard.
   - **Linux**: Download the `.deb` or `.rpm` file and install it using your package manager:
     ```bash
     sudo dpkg -i [package-name].deb
     ```
     or
     ```bash
     sudo rpm -i [package-name].rpm
     ```

For more details, refer to the [published paper](https://doi.org/10.32628/CSEIT2174128).
