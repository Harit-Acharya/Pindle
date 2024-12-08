# PINDLE: FUSE-based Filesystem and Folder Syncer

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
     sudo dpkg -i pindle.deb
     ```
     or
     ```bash
     sudo rpm -i pindle.rpm
     ```

@article{pindle2021,
  title={PINDLE: FUSE-based Filesystem and Folder Syncer},
  author={Parth Gor, Rayson D'sa, Harit Acharya, Mrs. Geetha S.},
  journal={International Journal of Scientific Research in Computer Science, Engineering and Information Technology},
  volume={7},
  issue={4},
  pages={561--566},
  year={2021},
  doi={10.32628/CSEIT2174128}
}

More info @ https://pindleproject.github.io/pindle.tech/
